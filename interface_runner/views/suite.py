import datetime
import openpyxl
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from interface_runner import models, serializers

from rest_framework.response import Response
from interface_runner.utils import response
from interface_runner.utils import prepare
from FasterRunner.utils.decorator import request_log
from interface_runner.utils.do_excel import DoExcel
from interface_runner.utils.import_case import CaseSwitchForImportCases


class TestCaseView(GenericViewSet):
    queryset = models.CaseSuit.objects
    serializer_class = serializers.CaseSuitSerializer
    tag_options = {
        "冒烟用例": 1,
        "集成用例": 2,
        "监控脚本": 3
    }

    @staticmethod
    def case_step_search(search):
        """
        搜索case_step的url或者name
        返回对应的case_id
        """
        case_id = models.CaseSuitInfo.objects.filter(Q(name__contains=search) | Q(url__contains=search)).values(
            'case_id')

        case_id = set([item['case_id'] for _, item in enumerate(case_id)])
        return case_id

    @method_decorator(request_log(level='INFO'))
    def get(self, request):
        """
        查询指定CASE列表，不包含CASE STEP
        {
            "project": int,
            "node": int
        }
        前端传递：http://172.25.105.54:8000/api/interface_runner/test/?project=7&node=&search=&searchType=1&caseType=&onlyMe=true
        序列化解析后：{'project': ['7'], 'node': [''], 'search': [''], 'searchType': ['1'], 'caseType': [''], 'onlyMe': ['true']}
        """
        ser = serializers.CaseSearchSerializer(data=request.query_params)
        if ser.is_valid():
            node = ser.validated_data.get("node")
            project = ser.validated_data.get("project")
            search = ser.validated_data.get("search")
            search_type = ser.validated_data.get("searchType")
            case_type = ser.validated_data.get("caseType")
            only_me = ser.validated_data.get("onlyMe")
            env_id = ser.validated_data.get("env_id")

            # update_time 降序排列
            # project="1"
            queryset = self.get_queryset().filter(project_id=project, env_id=env_id).order_by(
                '-update_time')  # 默认根据project查询

            if only_me is True:  # 权限配置，仅看到自己的用例，根据用户名过滤
                queryset = queryset.filter(creator=request.user)

            if node != '':
                queryset = queryset.filter(relation=node)

            if case_type != '':
                queryset = queryset.filter(case_tag=case_type)

            if search != '':
                # 用例名称搜索
                if search_type == '1':
                    queryset = queryset.filter(suit_name__contains=search)  # contains表示数据库查询里面的like，精确到大小写
                # API名称或者API URL搜索
                elif search_type == '2':
                    case_id = self.case_step_search(search)
                    queryset = queryset.filter(pk__in=case_id)

            pagination_query = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pagination_query, many=True)
            # res_data:[OrderedDict([('id', 192), ('tag', '集成用例'), ('create_time', '2020-12-12T14:18:48.235307'), ('update_time', '2020-12-12T14:20:12.592892'), ('creator', 'test'), ('updater', 'test'), ('name', '登录-登录成功'), ('relation', 6), ('length', 2), ('project', 7)]), OrderedDict([('id', 193), ('tag', '集成用例'), ('create_time', '2020-12-12T14:19:36.749762'), ('update_time', '2020-12-12T14:19:36.749787'), ('creator', 'test'), ('updater', None), ('name', '登录=登录失败'), ('relation', 6), ('length', 3), ('project', 7)])]
            res_data = serializer.data
            return self.get_paginated_response(res_data)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(request_log(level='INFO'))
    def copy(self, request, **kwargs):
        """
        pk int: test id
        {
            name: test name
            relation: int
            project: int
        }
        页面上复制suit的功能，总预览复制
        请求body：{"name":"登录=登录失败000","relation":"","project":"7"}
        """
        pk = kwargs['pk']  # pk为url中传递过来的int类型，比如192，kwargs={'pk':193}，也是数据库表case里面的主键id
        name = request.data['name']
        username = request.user.username  # 获取操作用户名，如：test
        if '|' in name:
            resp = self.split_rq(pk, name)
        else:
            # 执行存储过程数据收集
            case = models.CaseSuit.objects.get(id=pk)
            case.id = None
            case.name = name
            case.creator = username
            case.updater = username
            case.save()

            case_step = models.CaseSuitInfo.objects.filter(
                case__id=pk)  # 从case_step里面获取数据对应case_id的用例数据，并通过轮询遍历的方式存储在表中

            for step in case_step:
                step.id = None
                step.case = case
                step.creator = username
                step.updater = username
                step.save()
            resp = response.CASE_ADD_SUCCESS

        return Response(resp)

    def split_rq(self, pk, name):
        split_case_name = name.split('|')[0]
        split_condition = name.split('|')[1]

        # 更新原本的case长度
        case = models.CaseSuit.objects.get(id=pk)
        case_step = models.CaseSuitInfo.objects.filter(case__id=pk, name__icontains=split_condition)
        # case_step = case_step.filter(Q(method='config') | Q(name__icontains=split_condition))
        case_step_length = len(case_step)
        case.case_count -= case_step_length
        case.save()

        new_case = models.CaseSuit.objects.filter(name=split_case_name).last()
        if new_case:
            new_case.length += case_step_length
            new_case.save()
            case_step.update(case=new_case)
        else:
            # 创建一条新的case
            case.id = None
            case.name = split_case_name
            case.length = case_step_length
            case.save()

            # 把原来的case_step中的case_id改成新的case_id
            case_step.update(case=case)
        # case_step.filter(name=).update_or_create(defaults={'case_id': case.id})
        return response.CASE_SPILT_SUCCESS

    @method_decorator(request_log(level='INFO'))
    def patch(self, request, **kwargs):
        """
        更新测试用例集suit
        {
            suit_name: str
            id: int
            body: []
            project: int
            case_count:int
            case_tag:int
        }
        """

        pk = kwargs['pk']
        project = request.data.pop("project")
        body = request.data.pop('body')
        relation = request.data.pop("relation")
        env_id = request.data.pop("env_id")

        if models.CaseSuit.objects.exclude(id=pk). \
                filter(suit_name=request.data['suit_name'],
                       project__id=project,
                       relation=relation).first():
            return Response(response.CASE_EXISTS)

        case = models.CaseSuit.objects.get(id=pk)

        prepare.update_Case_suit_info(body, case, project, env_id, username=request.user.username)  # prepare为数据处理

        request.data['case_tag'] = self.tag_options[request.data['case_tag']]
        models.CaseSuit.objects.filter(id=pk).update(update_time=datetime.datetime.now(), updater=request.user.username,
                                                     **request.data)
        # 此种方法适合批量更新数据库，**request.data为以字典键值对方式添加数据库。若要单条数据添加，则使用save更好，save可以自动更新update_time

        return Response(response.CASE_UPDATE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def move(self, request):
        project: int = request.data.get('project')
        relation: int = request.data.get('relation')
        cases: list = request.data.get('case')
        ids = [case['id'] for case in cases]
        try:
            models.CaseSuit.objects.filter(
                project=project,
                id__in=ids).update(
                relation=relation)
        except ObjectDoesNotExist:
            return Response(response.CASE_NOT_EXISTS)

        return Response(response.CASE_UPDATE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def post(self, request):
        """
        新增测试用例集
        {
            name: str
            project: int,
            relation: int,
            tag:str
            body: [{
                id: int,
                project: int,
                name: str,
                method: str,
                url: str,
                source_api_id: int
            }]
        }
        """

        try:
            pk = request.data['project']
            request.data['project'] = models.Project.objects.get(id=pk)
            env_id = request.data['env_id']
            suit_name = request.data['suit_name']
            relation = request.data['relation']

            if models.CaseSuit.objects.filter(suit_name=suit_name, env_id=env_id, project=pk, relation=relation):
                return Response(response.CASE_EXISTS)


        except KeyError:
            return Response(response.KEY_MISS)

        except ObjectDoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)

        body = request.data.pop('body')

        request.data['case_tag'] = self.tag_options[request.data['case_tag']]
        with transaction.atomic():  # 保证所有数据库操作，都在一个事务中
            save_point = transaction.savepoint()
            case = models.CaseSuit.objects.create(**request.data, creator=request.user.username)
            try:
                prepare.generate_case_suit_info(body, case, env_id, request.user.username)
            except ObjectDoesNotExist:
                transaction.savepoint_rollback(save_point)
                return Response(response.CONFIG_MISSING)
        # 多余操作
        # case = models.Case.objects.filter(**request.data).first()

        # 不用多对多关系也能实现
        # case_step中的所有api_id
        # api_ids: set = prepare.generate_casestep(body, case, request.user.username)
        # apis = models.API.objects.filter(pk__in=api_ids).all()
        # case.apis.add(*apis)
        transaction.savepoint_commit(save_point)
        return Response(response.CASE_ADD_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def delete(self, request, **kwargs):
        """
        pk: test id delete single
        [{id:int}] delete batch
        """
        pk = kwargs.get('pk')

        try:
            if pk:
                prepare.case_end(pk)
            else:
                case_ids: list = []
                for content in request.data:
                    case_ids.append(content['id'])
                prepare.case_end(case_ids)

        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

        return Response(response.CASE_DELETE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def put(self, request, **kwargs):
        # case_id
        pk = kwargs['pk']

        # 在case_step表中找出case_id对应的所有记录,并且排除config
        api_id_list_of_dict = list(
            models.CaseSuitInfo.objects.filter(case_id=pk).exclude(method='config').values('source_api_id', 'step'))

        # 通过source_api_id找到原来的api
        # 把原来api的name, body, url, method更新到case_step中
        for item in api_id_list_of_dict:
            source_api_id: int = item['source_api_id']
            # 不存在api_id的直接跳过
            if source_api_id == 0:
                continue
            step: int = item['step']
            source_api = models.API.objects.filter(pk=source_api_id).values("interface_name", "body", "interface_path",
                                                                            "method").first()
            if source_api is not None:
                models.CaseSuitInfo.objects.filter(case_id=pk, source_api_id=source_api_id, step=step).update(
                    **source_api)
        models.CaseSuit.objects.filter(pk=pk).update(update_time=datetime.datetime.now())
        return Response(response.CASE_STEP_SYNC_SUCCESS)


class CaseSuitInfoView(GenericViewSet):
    """
    测试用例step操作视图
    """

    @method_decorator(request_log(level='INFO'))
    def get(self, request, **kwargs):
        """
        返回用例集信息
        """
        pk = kwargs['pk']

        queryset = models.CaseSuitInfo.objects.filter(case__id=pk).order_by('step')

        serializer = serializers.CaseSuitInfoSerializer(instance=queryset, many=True)

        resp = {
            "case": serializers.CaseSuitSerializer(instance=models.CaseSuit.objects.get(id=pk), many=False).data,
            "step": serializer.data
        }
        return Response(resp)

    # @method_decorator(request_log(level='INFO'))
    def upload_excel(self, request):
        """
        测试用例批量导入
        :param request:
        :return:
        """
        file = request.FILES['file']
        file_name = request.data['file_name']
        suit_name = request.data['suite_name']
        project = request.data['project']
        env_id = request.data['env_id']
        case_node = request.data['node']
        api_tree = request.data['api_tree']

        if not file_name.endswith('.xlsx'):
            return Response(response.EXCEL_UPLOAD_FORMAT_FAIL)

        excel_obj = CaseSwitchForImportCases(file=file)
        import_api_template_list = []
        import_case_list = []

        api_tree_id = None
        try:
            case_list, api_list = excel_obj.make_case()
            project_queryset = models.Project.objects.get(id=project)
            api_tree_queryset = models.Relation.objects.get(type=1, project_id=project).tree

            # ---api批量导入过程----
            if api_tree_queryset:
                for tree in eval(api_tree_queryset):
                    if api_tree == tree['label']:
                        api_tree_id = tree['id']  # 获取api分组id
                        break

            for api_template in api_list:
                api_template_dict = {
                    'interface_name': api_template['interface_name'],
                    'method': api_template['request']['method'],
                    'interface_path': api_template['request']['interface_path'],
                    'body': api_template,
                    'relation': api_tree_id,
                    'project': project_queryset,
                    'creator': request.user.username,
                    'type': 1,
                }
                api_template_obj = models.API(**api_template_dict)
                import_api_template_list.append(api_template_obj)

            models.API.objects.bulk_create(import_api_template_list)  # 批量导入api数据库

            # ---suite新增或识别过程----
            suite_queryset = models.CaseSuit.objects.filter(suit_name=suit_name, project=project, env_id=env_id,
                                                            relation=case_node).values('id', 'case_count')
            if suite_queryset:
                step_obj = models.CaseSuitInfo.objects.filter(case_id=suite_queryset[0]['id']).values('step')
                max_index = step_obj.count() - 1
                max_step = step_obj[max_index]['step'] + 1  # queryset无法使用负索引，所以只能计算出数量，取最大的索引获取step
                models.CaseSuit.objects.filter(suit_name=suit_name, project=project, env_id=env_id).update(
                    suit_name=suit_name,
                    case_count=suite_queryset[0]['case_count'] + len(case_list))
            else:
                suit_data = {
                    "project": project_queryset,
                    "relation": case_node,
                    "env_id": env_id,
                    "suit_name": suit_name,
                    "case_tag": 2,
                    "case_count": len(case_list),
                    "creator": request.user.username
                }
                max_step = 1
                models.CaseSuit.objects.create(**suit_data)

            suite_queryset = models.CaseSuit.objects.get(suit_name=suit_name, project=project, env_id=env_id,
                                                         relation=case_node)

            # ---case_suite_info批量导入过程----

            for case_data in case_list:
                # 查询api模板id
                api_id = models.API.objects.filter(interface_path=case_data['request']['interface_path'], type=1,
                                                   interface_name=case_data['interface_name'],
                                                   creator=request.user.username).order_by('-create_time').values('id')
                case_dict = {
                    "case_name": case_data['interface_name'],
                    "body": case_data,
                    "interface_path": case_data['request']['interface_path'],
                    "method": case_data['request']['method'],
                    "step": max_step,
                    "case": suite_queryset,  # 就是case_id
                    "source_api_id": api_id[0]['id'],  # 默认取最近生成的第一个同样接口路由的用例
                    "creator": request.user.username,
                    "env_id": env_id,
                    "type": 1,
                }
                max_step = max_step + 1
                case_obj = models.CaseSuitInfo(**case_dict)
                import_case_list.append(case_obj)

            models.CaseSuitInfo.objects.bulk_create(import_case_list)  # 批量导入

            return Response(response.EXCEL_IMPORT_SUCCESS)

        except Exception as e:
            import traceback
            resp = response.EXCEL_UPLOAD_FAIL
            resp['msg'] = f"导入数据过程中发生异常，请检查\n{traceback.format_exc()}"
            return Response(resp)
