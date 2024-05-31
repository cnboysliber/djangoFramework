# -*- coding: utf-8 -*-
import os
import tempfile

from django.conf import settings
from django.http import StreamingHttpResponse
from django.utils.encoding import escape_uri_path
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser

from FasterRunner import pagination
from FasterRunner import const as cnt
from FasterRunner.utils.logging import logger
from FasterRunner.utils.decorator import request_log
from performApp import models
from performApp import serializers
from performApp.utils import response
from performApp.utils.jmeterApi import JmRest


class PerformScriptView(GenericViewSet):
    """
    Script-脚本文件接口视图
    """
    queryset = models.PerformScript.objects
    serializer_class = serializers.PerformScriptSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        Script-查询列表

        :param request:
        :return:
        """

        page_size = int(request.query_params.get('pageSize', 10))
        page_number = int(request.query_params.get('pageNumber', 1))
        jmt = JmRest()
        body = {
            'sceneId': request.query_params.get('sceneUid', None),
            'pageSize': page_size,
            'pageNumber': page_number,
        }
        files_data = jmt.get_script_list(body)
        file_data = files_data['data']
        count = files_data['total']
        result = {
            'code': '000000',
            'msg': '查询成功',
            'results': file_data,
            'count': count
        }
        return Response(result)

    def get_detail(self, request, **kwargs):
        """
        Script-查询详情

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
        Script-添加

        :param request:
        :return:
        """
        # 反序列化
        context = {
            "request": self.request,
        }
        scene_uid = request.data.get('scene_uid')
        filename = request.data.get('name')
        file_type = request.data.get('file_type')
        action = request.data.get('action')
        jmt = JmRest()
        file = request.FILES['file']
        fp = tempfile.TemporaryFile('wb+')
        try:
            upload_success = True
            error = ''
            data = file.read()
            fp.write(data)
            fp.seek(0)
            files = [
                ('file', (filename, fp, 'application/octet-stream'))
            ]
            file_data = jmt.upload_jmt_script(scene_uid, files)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            upload_success = False
            error = str(e)
            logger.error(str(e))
            raise Exception('操作失败')
        finally:
            fp.close()

        # 上传文件失败
        if not upload_success:
            ret = response.SYSTEM_ERROR
            ret.update({'msg': str(error)})
            return Response(ret)
        return Response(file_data)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        Script-单个删除

        :param request:
        :return:
        """
        # 反序列化
        jmt = JmRest()
        body = {
            'sceneId': request.data.get('sceneId'),
            'fileName': request.data.get('fileName'),
            'fileId': request.data.get('fileId')
        }
        del_script = jmt.del_script(body)
        results = {
            'code': '000000',
            'msg': '删除成功',
            'results': del_script,
            }
        return Response(results)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request):
        """
        Script-批量删除

        :param request:
        :return:
        """
        # 反序列化
        jmt = JmRest()
        count = 0  # 计算删除文件个数
        # 获取请求列表后还原字符串类型，为字典
        res_list = [eval(v) for v in request.query_params.values()]
        for res in res_list:
            body = {
                'sceneId': res.get('sceneId'),
                'fileName': res.get('fileName'),
                'fileId': res.get('fileId')
            }
            del_script = jmt.del_script(body)
            count += 1
        results = {
            'code': '000000',
            'msg': '批量删除成功',
            'results': del_script,
            'count': count
        }
        return Response(results)

    @method_decorator(request_log(level='INFO'))
    def down_script(self, request, **kwargs):
        """
        Script-文件下载

        :param request:
        :return:
        """
        # 反序列化
        fileName = request.query_params.get('fileName')
        sceneId = request.query_params.get('sceneId')
        jmt = JmRest()
        body = {
            'sceneId': sceneId,
            'name': fileName,
        }
        content = jmt.down_script(body)
        fp = tempfile.TemporaryFile('wb+')
        fp.write(content)
        fp.seek(0)
        fresponse = StreamingHttpResponse(fp)
        fresponse['filename'] = fileName
        fresponse['Content-Type'] = 'application/octet-stream'
        fresponse['Access-Control-Expose-Headers'] = "Content-Disposition, Content-Type"
        fresponse['Content-Disposition'] = f"attachment; filename={escape_uri_path(fileName)}"

        return fresponse

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        Script-更新

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            scene_uid = request.data.get('scene_uid')
            jmt = JmRest()
            fdata = self.queryset.get(id=pk).data
            fp = tempfile.TemporaryFile('wb+')
            try:
                upload_success = True
                error = ''
                fp.write(fdata.encode())
                fp.seek(0)
                files = [
                    ('file', ('test.jmx', fp, 'application/octet-stream'))
                ]
                jmt.upload_jmt_script(scene_uid, files)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                upload_success = False
                error = str(e)
                logger.error(str(e))
            finally:
                fp.close()

            # 上传文件失败
            if not upload_success:
                ret = response.SYSTEM_ERROR
                ret.update({'msg': str(error)})
                return Response(ret)

            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            return Response(response.PROJECT_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def upload_script(self, request, **kwargs):
        """
        Script-脚本文件上传

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        file = request.FILES['file']
        file_name = file.name.strip('.jmx')
        if not file.name.endswith('.jmx'):
            return Response(response.PERFORM_TYPE_ERROR)

        content = file.read()
        jmt_dir = os.path.join(settings.JMT_PATH, 'script'.format(pk))
        script_path = os.path.join(jmt_dir, '{}-{}.jmx'.format(file_name, pk))
        if not os.path.exists(jmt_dir):
            os.makedirs(script_path)

        # 保存jtl文件
        with open(script_path, 'wb') as fp:
            fp.write(content)

        return Response(response.PERFORM_UPLOAD_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def copy_script(self, request, **kwargs):
        """
        scene-copy场景脚本
        :param request:
        :return:
        """
        print(5555555555555555, request)
        context = {
            "request": self.request,
        }
        try:
            for file in request.data.files:
                data = {
                    "scene_uid": request.data.scene_uid,
                    "name": file['name'],
                    "file_type": file['file_type']
                }
                serializer = self.serializer_class(data=data, context=context)
                if serializer.is_valid():
                    serializer.save()
            return Response(response.SCENES_COPY_SUCCESS)
        except:
            logger.error(serializer.errors)
            ret = response.SYSTEM_ERROR
            ret.update({'msg': serializer.errors})
            return Response(ret)


class PerformScriptParamsView(GenericViewSet):
    """
    ScriptParams-参数化文件接口类视图
    """
    queryset = models.PerformScriptParams.objects
    serializer_class = serializers.PerformScriptParamsSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        ScriptParams-查询列表

        :param request:
        :return:
        """

        filters = dict({})
        filters['script_id'] = request.query_params.get('script_id', '')
        filters['name__contains'] = request.query_params.get('name', '')

        queryset = self.queryset.filter(status=cnt.ACTIVE)

        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def download(self, request):
        """
        ScriptParams-下载

        :param request:
        :return:
        """
        # 反序列化

        queryset = self.queryset.filter(uid=request.query_params.get('uid', ''), status=cnt.ACTIVE).first()

        filename = 'jmeter.log'
        test_fp = open(os.path.join(settings.BASE_DIR, filename), 'rb')
        fresponse = StreamingHttpResponse(test_fp)

        # 增加headers
        fresponse['filename'] = filename
        fresponse['Content-Type'] = 'application/octet-stream'

        fresponse['Access-Control-Expose-Headers'] = "Content-Disposition, Content-Type"

        fresponse['Content-Disposition'] = "attachment; filename={}".format(escape_uri_path(filename))

        return fresponse

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        ScriptParams-单个删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.PROJECT_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def upload_script(self, request, **kwargs):
        """
        ScriptParams-脚本文件上传

        :param request:
        :return:
        """
        # 反序列化
        context = {
            "request": self.request,
        }
        serializer = self.serializer_class(data=request.data, context=context)

        if not serializer.is_valid():
            logger.error(serializer.errors)
            ret = response.SYSTEM_ERROR
            ret.update({'msg': serializer.errors})
            return Response(ret)

        pk = kwargs.get('pk')
        file = request.FILES['file']
        file_name = file.name.strip('.jmx')
        if not file.name.endswith('.jmx'):
            return Response(response.PERFORM_TYPE_ERROR)

        content = file.read()
        jmt_dir = os.path.join(settings.JMT_PATH, 'script'.format(pk))
        script_path = os.path.join(jmt_dir, '{}-{}.jmx'.format(file_name, pk))
        if not os.path.exists(jmt_dir):
            os.makedirs(script_path)

        # 保存jtl文件
        with open(script_path, 'wb') as fp:
            fp.write(content)

        return Response(response.PERFORM_UPLOAD_SUCCESS)




