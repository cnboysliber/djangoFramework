# -*- coding: utf-8 -*-
import json
import datetime
import tempfile

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import escape_uri_path
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from fastuser import models as u_model
from FasterRunner import const as cnt
from FasterRunner import pagination
from FasterRunner.threadpool import execute
from FasterRunner.utils import obj_to_dicts
from FasterRunner.utils.decorator import request_log
from FasterRunner.utils.logging import logger
from performApp import models
from performApp import serializers
from performApp.utils import error as err
from performApp.utils import response
from performApp.utils.celery_task import CeleryTask
from performApp.utils.jmeterApi import JmRest
from performApp.utils.exeTask import influxdb_run_task_data, Influx, run_task, get_influx_db_data


class PerformScenesView(GenericViewSet):
    """
    Scenes-性能场景增删改查
    """
    queryset = models.ScenesManage.objects
    serializer_class = serializers.ScenesManageSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def list(self, request):
        """
        Scenes-查询列表

        :param request:
        :return:
        """
        filters = dict({})
        filters['item__in'] = request.query_params.get('item') or [1, 2, 3]
        filters['sType__in'] = request.query_params.get('sType') or [1, 2]
        filters['scene_name__contains'] = request.query_params.get('scene_name', '')
        scene_id = request.query_params.get('sceneId')
        project_id = request.query_params.get('projectId')
        real_name = request.query_params.get('realName')
        user = u_model.MyUser.objects.filter(first_name=real_name, is_active=1).first()
        if real_name:
            filters['creator'] = user.creator
        if project_id:
            filters['project_id'] = project_id
        if scene_id:
            filters['id'] = scene_id

        keyword = request.query_params.get("keyword", '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-create_time')

        if request.query_params != '':
            queryset = queryset.filter(Q(scene_name__contains=keyword) |
                                       Q(creator__contains=keyword) |
                                       Q(remark__contains=keyword))\
                .filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def get_detail(self, request, **kwargs):
        """
        Scenes-查询详情

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        queryset = self.queryset.filter(id=pk, status=cnt.ACTIVE).first()
        serializer = self.get_serializer(queryset)

        return Response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        Scenes-添加

        :param request:
        :return:
        """
        # 反序列化
        context = {
            "request": self.request,
        }
        body = {
            'sceneName': request.data.get('scene_name'),
            'createBy': request.user.username,
            'remark': request.data.get('remark'),
        }
        rest = JmRest()
        resp = rest.add_scene(**body)
        data = request.data.copy()
        data['scene_uid'] = resp.get('sceneId')
        serializer = self.serializer_class(data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(response.PROJECT_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def copy_scenes(self, request, **kwargs):
        # 反序列化
        context = {
            "request": self.request,
        }
        body = {
            "scene_uid": request.data.get('scene_uid'),
            "creator": request.data.get('creator'),
        }
        rest = JmRest()
        resp = rest.copy_scenes(body)

        # request = serializers.ScenesManageSerializer.get_update_info(request)
        data = request.data.copy()
        data['scene_uid'] = resp.get('sceneId')
        data['scene_name'] = resp.get('sceneName')
        serializer = self.serializer_class(data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(response.SCENES_COPY_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        Scenes-单个删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.UNAUTHORIZED_ERROR)
        try:
            scene = self.queryset.get(id=kwargs['pk'])
            jmt = JmRest()
            jmt.del_scene(scene.scene_uid)
            models.PerformScript.objects.filter(scene_uid=scene.scene_uid).update(status=cnt.NOT_ACTIVE)
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)

            return Response(response.PROJECT_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request):
        """
        Scenes-批量删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.UNAUTHORIZED_ERROR)
        try:
            scene_uids = self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values())))
            jmt = JmRest()
            for scene_uid in scene_uids:
                jmt.del_scene(scene_uid)
            models.PerformScript.objects.filter(scene_uid__in=scene_uids).update(status=cnt.NOT_ACTIVE)
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.PROJECT_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        Scenes-更新

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {}
            for k, v in dict(request.data).items():
                if (k == 'script_id' and not v[0]) or (k == 'plan_time' and request.data.get('interval') == '0'):
                    continue
                update_kw[k] = v[0]
            self.queryset.filter(id=pk).update(**update_kw)
            scene_uid = self.queryset.get(id=pk).scene_uid
            jmt = JmRest()
            data = {
                'sceneId': scene_uid,
                'sceneName': request.data.get('scene_name'),
                'updateBy': request.user.username,
                'remark': request.data.get('remark'),
            }
            jmt.update_scene(data)
            return Response(response.SCENES_CONFIG_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def run_task(self, request):
        """
        运行场景压测
        :param request:
        :return:
        """
        scene_id = request.data.get('sceneId')
        scene_uid = self.queryset.get(id=scene_id, status=cnt.ACTIVE).scene_uid
        jmt = JmRest()
        body = {
            'sceneId': scene_uid,
            'numThreads': request.data.get('numThreads'),
            'numNode': request.data.get('numNode'),
            'stressTime': request.data.get('stressTime'),
            'rameUp': request.data.get('rameUp'),
            'isGlobal': request.data.get('isGlobal'),
            'flowModel': request.data.get('flowModel')
        }
        run_times = int(request.data.get('runTimes', 1))
        try:
            if jmt.exist_jconfig(scene_uid):
                jmt.update_jconfig(body)
            else:
                jmt.add_jconfig(body)
            # return Response(response.SCENES_CONFIG_UPDATE_SUCCESS)
        except Exception as e:
            logger.error(f'更新失败！{e}')
        else:
            sc_resp = response.SCENES_RUN_SUCCESS
            runner = request.user.username
            if run_times < 2:
                resp = jmt.run_scene(scene_uid, runner)
                if not resp['data']:
                    raise err.AppError(500, '压测任务执行失败')
                task_id = resp['data']
                execute.submit(influxdb_run_task_data, task_id)
            else:
                execute.submit(run_task, scene_uid, runner, run_times)
                task_id = None
            sc_resp['taskId'] = task_id
            return Response(sc_resp)

    @method_decorator(request_log(level='INFO'))
    def stop_task(self, request):
        """
        停止场景压测
        :param request:
        :return:
        """
        scene_id = request.data.get('sceneId')
        scene_uid = self.queryset.get(id=scene_id, status=cnt.ACTIVE).scene_uid
        jmt = JmRest()
        resp = jmt.stop_scene(scene_uid)
        sc_resp = response.SCENES_STOP_SUCCESS
        sc_resp['data'] = resp
        return Response(sc_resp)

    @method_decorator(request_log(level='INFO'))
    def add_jconfig(self, request):
        """
        Scenes-新增配置信息

        :param request:
        :return:
        """
        # 反序列化
        scene_uid = self.queryset.get(id=request.data.get('sceneId')).scene_uid
        body = {
            'sceneId': scene_uid,
            'numThreads': request.data.get('numThreads'),
            'numNode': request.data.get('numNode'),
            'stressTime': request.data.get('stressTime'),
            'rameUp': request.data.get('rameUp'),
            'isGlobal': request.data.get('isGlobal'),
            'flowModel': request.data.get('flowModel'),
            'createBy': request.user.username,
        }
        rest = JmRest()
        rest.add_jconfig(body)
        return Response(response.SCENES_CONFIG_ADD_SUCCESS)

    @method_decorator(request_log(level='DEBUG'))
    def get_jconfig(self, request, **kwargs):
        """
        查询配置详情
        :param request:
        :return:
        """
        scene_uid = self.queryset.get(id=kwargs['pk']).scene_uid
        rest = JmRest()
        result = rest.get_jconfig_detail(scene_uid)
        return Response(result)

    @method_decorator(request_log(level='INFO'))
    def patch_jconfig(self, request, **kwargs):
        """
        Scenes-更新配置信息

        :param request:
        :return:
        """
        # 反序列化
        scene_uid = self.queryset.get(id=kwargs.get('pk')).scene_uid
        body = {
            'sceneId': scene_uid,
            'numThreads': request.data.get('numThreads'),
            'numNode': request.data.get('numNode'),
            'stressTime': request.data.get('stressTime'),
            'rameUp': request.data.get('rameUp'),
            'isGlobal': request.data.get('isGlobal'),
            'flowModel': request.data.get('flowModel')
        }
        rest = JmRest()
        if rest.exist_jconfig(scene_uid):
            rest.update_jconfig(body)
        else:
            rest.add_jconfig(body)
        return Response(response.SCENES_CONFIG_UPDATE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def remark_task(self, request):
        """
        标记任务信息
        :param request:
        :return:
        """
        rest = JmRest()
        rest.task_remark(**request.data.dict())
        task_id = request.data.get('taskId')
        task_data_exist = models.PerformJmeterData.objects.filter(task_id=task_id).first()
        if not task_data_exist:
            execute.submit(influxdb_run_task_data, task_id, request.data.get('flag'))
        else:
            models.PerformJmeterData.objects.filter(task_id=task_id)\
                .update(flag=request.data.get('flag'), scene_id=request.data.get('sceneId'))
        return Response(response.REMARK_TASK_SUCCESS)

    @method_decorator(request_log('DEBUG'))
    def get_task_list(self, request):
        """
        查询task列表
        :param request:
        :return:
        """
        project_id = request.query_params.get('projectId')
        scene_name = request.query_params.get('sceneName')
        version = request.query_params.get('version')
        page_size = int(request.query_params.get('pageSize', 10))
        page_number = int(request.query_params.get('pageNumber', 1))
        view = request.query_params.get('view')
        jmt = JmRest()
        body = {
            'flag': request.query_params.get('flag', None),
            'sceneId': request.query_params.get('sceneId', None),
            'pageSize': page_size,
            'pageNumber': page_number,
        }
        tasks = jmt.get_jtask_list(body)
        task_data = tasks['data']
        count = tasks['total']
        scene_uids = [x['sceneId'] for x in task_data]
        user_id_lst = [x['runBy'] for x in task_data]
        filters = dict(project_id=project_id) if project_id else {}
        if scene_name:
            filters.update({'scene_name': scene_name})
        if version:
            filters.update({'version': version})
        scene_obj_lst = models.ScenesManage.objects.filter(scene_uid__in=scene_uids, **filters, status=cnt.ACTIVE)
        scene_uid2obj = {obj.scene_uid: obj for obj in scene_obj_lst}
        project_ids = [scene.project_id for scene in scene_obj_lst]
        project_obj_lst = models.PerformProject.objects.filter(id__in=project_ids)
        project_id2obj = {obj.id: obj for obj in project_obj_lst}
        user_obj_lst = serializers.User.objects.filter(username__in=user_id_lst)
        user_id2name = {x.username:  x.first_name for x in user_obj_lst}
        task_list = []
        for task in task_data:
            scene = scene_uid2obj.get(task['sceneId'])
            if scene:
                task['sceneName'] = scene.scene_name
                project_id = scene.project_id
                task['version'] = scene.version
                task['projectId'] = project_id
                task['project'] = project_id2obj.get(project_id).project
            else:
                task['version'] = ''
                task['project'] = ''
            task['runBy'] = user_id2name.get(task['runBy'], task['runBy'])

            task['interfaces'] = []
            int2float = ['avg', 'pct90', 'pct95', 'pct99', 'tps', 'req_count', 'req_err_count']
            task_interfaces = models.PerformJmeterData.objects.filter(task_id=task['taskId']).all()

            task_interfaces = obj_to_dicts(task_interfaces, ['task_id', 'transaction',
                                                             'avg', 'pct90', 'pct95', 'pct99',
                                                             'req_count', 'req_err_count', 'tps'])
            if not task_interfaces:
                task_interfaces = get_influx_db_data(task['taskId'])
            if task_interfaces:
                task_interfaces = sorted([dict(t) for t in set([tuple(d.items()) for d in task_interfaces])],
                                         key=lambda x: x['req_count'])[::-1]
                for interface in task_interfaces:
                    interface_info = {k: round(v / 100, 2) if k in int2float else v for k, v in interface.items()}
                    interface_info['sceneName'] = task['sceneName']
                    interface_info['version'] = task['version']
                    interface_info['numThreads'] = task['numThreads']

                    err_pct = interface_info.get('req_err_count', 0) * 100 / interface_info.get('req_count')
                    interface_info['errPct'] = '%.2f' % (err_pct,)
                    if interface['transaction'] == 'all':
                        task.update(interface_info)
                        task['transaction'] = 'ALL'
                    if not (view and interface['transaction'] == 'all'):
                        task['interfaces'].append(interface_info)
                task['interfaces'] = sorted(task['interfaces'], key=lambda x: x['transaction'])
                task_list.append(task)

        result = {
            'code': '000000',
            'msg': '查询成功',
            'data': task_list,
            'count': count
        }
        return Response(result)

    @method_decorator(request_log(level='DEBUG'))
    def get_tps_chart_data(self, request):
        """
        获取图标数据
        :param request:
        :return:
        """

        queryset = models.PerformResultView.objects.filter(transaction='all') \
            .order_by('-version', 'scene_name')
        scene_name_lst = sorted(list(set([x.scene_name.strip() for x in queryset])))
        chart_result_lst = []

        for column_type in ['tps', 'pct90']:
            queryset_lst = queryset.filter(scene_name__in=scene_name_lst)
            y_axis_name, title = (['TPS'], 'TPS-') if column_type == 'tps' else (['RT90/ms'], 'RT90响应时间-')

            result_data = obj_to_dicts(queryset_lst)
            int2float = ['avg', 'pct90', 'pct95', 'pct99', 'tps', 'req_count', 'req_err_count']

            pare_result = []
            columns = ['version'] + \
                      ['{}'.format(scene_name) for scene_name in scene_name_lst]
            for data in result_data:
                new_data = {k: round(v / 100, 2) if k in int2float else v for k, v in data.items()}
                new_data['errPct'] = round(new_data.get('req_err_count', 0) * 100 / new_data.get('req_count'), 2)
                pare_result.append(new_data)
            tmp_dict = {}
            for chart in pare_result:
                if chart['version'] not in tmp_dict:
                    tmp_dict[chart['version']] = {
                        'version': chart['version'],
                        '{}'.format(chart['scene_name']): chart[column_type]
                    }
                else:
                    tmp_dict[chart['version']].update({
                        '{}'.format(chart['scene_name']): chart[column_type]
                    })
            rows = []
            for version, chart in tmp_dict.items():
                rows.append(chart)
            chart_result_lst.append({'data': {'columns': columns, 'rows': rows},
                                     'yAxisName': y_axis_name, 'title': title})
        return Response({'data': chart_result_lst, 'success': True, 'msg': '查询成功'})

    @method_decorator(request_log(level='INFO'))
    def get_scene_transactions(self, request):
        """
        查询场景下的接口详情
        :param request:
        :return:
        """
        scene_id = request.data.get('sceneUid')
        jmt = JmRest()
        body = {
            'flag': 1,
            'sceneId': scene_id,
            'pageSize': 100,
            'pageNumber': 1,
        }
        task_list = jmt.get_jtask_list(body)

        task_id_lst = list(map(lambda x: x['taskId'], task_list['data']))
        transactions = models.PerformJmeterData.objects.filter(task_id__in=task_id_lst)
        transaction_lst = obj_to_dicts(transactions)
        return Response(transaction_lst)

    @method_decorator(request_log(level='INFO'))
    def get_perform_result(self, request):
        """
        查询性能报告结果
        :param request:
        :return:
        """
        query_all = json.loads(request.query_params.get('all', 'true'))
        project_id = request.query_params.get('projectId')
        scene_name = request.query_params.get('sceneName')
        version = request.query_params.get('version')
        task_id = request.query_params.get('taskId')
        filters = {}
        if project_id:
            filters.update({'project_id': project_id})
        if scene_name:
            filters.update({'scene_name': scene_name})
        if task_id:
            filters.update({'task_id': task_id})
        if version:
            filters.update({'version': version})

        queryset = models.PerformResultView.objects.filter(**filters)\
            .order_by('project_id', 'scene_name', 'version', 'transaction')
        if query_all:
            queryset = queryset.filter(transaction='all')
        else:
            queryset = queryset.exclude(transaction='all')
        pagination_queryset = self.paginate_queryset(queryset)
        result_data = obj_to_dicts(pagination_queryset)
        int2float = ['avg', 'pct90', 'pct95', 'pct99', 'tps', 'req_count', 'req_err_count']

        pare_result = []
        for data in result_data:
            new_data = {k: round(v / 100, 2) if k in int2float else v for k, v in data.items()}
            new_data['errPct'] = round(new_data.get('req_err_count', 0) * 100 / new_data.get('req_count'), 2)
            pare_result.append(new_data)
        return self.get_paginated_response(pare_result)

    @method_decorator(request_log(level='INFO'))
    def download_error_log(self, request, **kwargs):
        """
        Script-文件下载

        :param request:
        :return:
        """
        # 反序列化
        scene_id = request.query_params.get('sceneId')
        task_id = request.query_params.get('taskId')
        scene_name = request.query_params.get('sceneName')
        jmt = JmRest()
        body = {
            'sceneId': scene_id,
            'taskId': task_id,
        }
        content = jmt.down_error_log(body)
        fp = tempfile.TemporaryFile('wb+')
        fp.write(content)
        fp.seek(0)
        fresponse = StreamingHttpResponse(fp)
        fresponse['filename'] = scene_name
        fresponse['Content-Type'] = 'application/octet-stream'
        fresponse['Access-Control-Expose-Headers'] = "Content-Disposition, Content-Type"
        fresponse['Content-Disposition'] = f"attachment; filename={escape_uri_path(scene_name)}"

        return fresponse

    @method_decorator(request_log(level='INFO'))
    def get_transaction_data(self, request):
        """
        获取接口的响应数据
        :param request:
        :return:
        """
        ret = Influx.get_application_data(**request.data)
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def get_scene_perform_report(self, request):
        """
        查询场景压测归档后的报告
        :param request:
        :return:
        """
        queryset = models.PerformJmeterData.objects.all()
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        data = self.get_paginated_response(serializer.data)


class PerformScenesPlanView(GenericViewSet):
    """
    Scenes-性能场景增删改查
    """
    queryset = models.ApiPerformancePlan.objects
    serializer_class = serializers.ApiPerformancePlanSerializer
    pagination_class = pagination.MyPageNumberPagination
    Admin = 'Admin'
    parser_classes = [FormParser, JSONParser]

    @method_decorator(request_log('DEBUG'))
    def patch_schedule_scene(self, request):
        """
        场景添加定时任务
        :param request:
        :return:
        """
        context = {
            "request": self.request,
        }
        if request.data.get('schedule') not in [1, 2]:
            Exception('不支持的任务类型')
        scene_obj = models.ScenesManage.objects.get(id=self.request.data.get('sceneId'))
        scene_id = request.data.get('sceneId')
        scene_uid = scene_obj.scene_uid
        task_exist = self.queryset.filter(scene_id=scene_id, status=cnt.ACTIVE).first()

        task_module = request.data.get('module') or 'performApp.tasks.scene_task'
        serializer_data = {
            'scene_id': scene_id,
            'plan_type': request.data.get('schedule'),
            'plan_time': request.data.get('time'),
            'module': task_module,
        }
        task_data = {
            'name': scene_uid,
            'time': request.data.get('time'),
            'type': 2,  # 都是用crontab方式设置定时任务
            'data': [scene_obj.scene_uid],
        }
        if task_exist:
            task_data['updater'] = request.user.username
        else:
            task_data['creator'] = request.user.username
        task = CeleryTask(**task_data)
        if int(request.data.get('schedule')) == 2:
            task.set_format_crontab(request.data.get('time'))
        else:
            format_time = request.data.get('time').split('|')[-1]
            date_time = datetime.datetime.strptime(format_time, '%H:%M')
            task.set_format_crontab(format_time,
                                    month='*', day='*/1',
                                    hour=date_time.hour, minute=date_time.minute, date_format='%H:%M')

        if task_exist:
            self.queryset.filter(scene_id=scene_id).update(**serializer_data)
            resp = task.update_task(scene_obj.scene_uid)
        else:
            serializer = self.serializer_class(data=serializer_data, context=context)
            if not serializer.is_valid():
                raise err.AppError(500, '请求数据不合法')

            serializer.save()
            resp = task.add_task(task_module)
        return Response(resp)

    @method_decorator(request_log('DEBUG'))
    def stop_schedule_scene(self, request):
        """
        停止场景定时任务
        :param request:
        :return:
        """
        scene_id = request.data.get('sceneId')
        scene = models.ScenesManage.objects.get(id=scene_id)
        self.queryset.filter(scene_id=scene_id).update(state=cnt.NOT_ACTIVE)

        task = CeleryTask(**request.data)
        resp = task.stop_task(scene.scene_uid)
        return Response(resp)

    @method_decorator(request_log('DEBUG'))
    def delete(self, request, **kwargs):
        """
        删除定时任务
        :param request:
        :param kwargs:
        :return:
        """
        scene_id = request.data.get('sceneId')
        scene = models.ScenesManage.objects.get(id=scene_id)
        self.queryset.filter(scene_id=scene_id).update(status=cnt.NOT_ACTIVE)
        task = CeleryTask(**request.data)
        resp = task.del_task(scene.scene_uid)

        return Response(resp)

