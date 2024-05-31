import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from interface_runner import models, serializers
from rest_framework.response import Response
from interface_runner.utils import response
from FasterRunner.utils.decorator import request_log
from interface_runner.utils.parser import Format, Parse
from django.db import DataError
from django.db.models import Q

from rest_framework.schemas import AutoSchema, SchemaGenerator
import coreapi


class APITemplateViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ('get',):
            extra_fields = [
                coreapi.Field('node'),
                coreapi.Field('project'),
                coreapi.Field('search'),
                coreapi.Field('tag'),
                coreapi.Field('rigEnv'),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class APITemplateView(GenericViewSet):
    """
    API操作视图
    """
    serializer_class = serializers.APISerializer
    queryset = models.API.objects
    schema = APITemplateViewSchema()

    @swagger_auto_schema(query_serializer=serializers.AssertSerializer)
    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        api-获取api列表

        支持多种条件搜索
        """
        ser = serializers.AssertSerializer(data=request.query_params)
        if ser.is_valid():
            node = ser.validated_data.get('node')
            project = ser.validated_data.get('project')
            search: str = ser.validated_data.get('search')
            tag = ser.validated_data.get('tag')
            rig_env = ser.validated_data.get('rigEnv')
            delete = ser.validated_data.get('delete')
            only_me = ser.validated_data.get('onlyMe')
            show_yapi = ser.validated_data.get('showYAPI')

            queryset = self.get_queryset().filter(project__id=project, delete=delete).order_by('-update_time')

            # if only_me is True:  #只可以新增这条api的用户可以看到对应api
            #     queryset = queryset.filter(creator=request.user)

            if show_yapi is False:
                queryset = queryset.filter(~Q(creator='yapi'))

            if search != '':
                search: list = search.split()
                for key in search:
                    queryset = queryset.filter(Q(interface_name__contains=key) | Q(interface_path__contains=key))

            if node != '':
                queryset = queryset.filter(relation=node)

            if tag != '':
                queryset = queryset.filter(tag=tag)

            if rig_env != '':
                queryset = queryset.filter(rig_env=rig_env)

            pagination_queryset = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pagination_queryset, many=True)

            return self.get_paginated_response(serializer.data)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        api-新增一个api

        前端按照格式组装好，注意body
        """

        api = Format(request.data)  #实例化
        api.parse()    #针对请求信息进行处理，然后生成属性testcase给下方api_body使用

        api_body = {
            'interface_name': api.interface_name,
            'body': api.testcase,
            'interface_path': api.interface_path,
            'method': api.method,
            'project': models.Project.objects.get(id=api.project),
            'relation': api.relation,
            'creator': request.user.username
        }

        try:
            models.API.objects.create(**api_body)   #create和save一样，都是新增存储意思
        except DataError:
            return Response(response.DATA_TO_LONG)

        return Response(response.API_ADD_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def update(self, request, **kwargs):
        """
        api-更新单个api

        更新单个api的内容
        """
        pk = kwargs['pk']
        api = Format(request.data)
        api.parse()

        api_body = {
            'interface_name': api.interface_name,
            'body': api.testcase,
            'interface_path': api.interface_path,
            'method': api.method,
            'updater': request.user.username
        }

        try:
            models.API.objects.filter(id=pk).update(**api_body)
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_UPDATE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def move(self, request):
        """
        api-批量更新api的目录

        移动api到指定目录
        """
        project: int = request.data.get('project')
        relation: int = request.data.get('relation')
        apis: list = request.data.get('api')
        ids = [api['id'] for api in apis]

        try:
            models.API.objects.filter(
                project=project,
                id__in=ids).update(
                relation=relation)
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_UPDATE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def copy(self, request, **kwargs):
        """
        api-复制api

        复制一个api
        """
        pk = kwargs['pk']
        name = request.data['interface_name']
        api = models.API.objects.get(id=pk)
        body = eval(api.body)
        body["interface_name"] = name
        api.body = body
        api.id = None
        api.interface_name = name
        api.creator = request.user.username
        api.updater = request.user.username
        api.save()
        return Response(response.API_ADD_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def delete(self, request, **kwargs):
        """
        api-删除一个api

        软删除一个api
        """

        try:
            if kwargs.get('pk'):  # 单个删除
                # models.API.objects.get(id=kwargs['pk']).delete()
                models.API.objects.filter(id=kwargs['pk']).update(delete=1, update_time=datetime.datetime.now())
            else:
                del_ids = [content['id'] for content in request.data]
                # for content in request.data:
                # models.API.objects.get(id=content['id']).delete()
                models.API.objects.filter(id__in=del_ids).update(delete=1)

        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_DEL_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def add_tag(self, request, **kwargs):
        """
        api-更新api的tag,暂时默认为调试成功

        更新api的tag类型
        """

        try:
            if kwargs.get('pk'):
                models.API.objects.filter(id=kwargs['pk']).update(tag=request.data['tag'],
                                                                  update_time=datetime.datetime.now(),
                                                                  updater=request.user.username)
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_UPDATE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def sync_case(self, request, **kwargs):
        """
        api-同步api的到case_step

        1.根据api_id查出("interface_name", "body", "url", "method")
        2.根据api_id更新case_step中的("name", "body", "url", "method", "updater")
        3.更新case的update_time, updater
        """
        pk = kwargs['pk']
        source_api = models.API.objects.filter(pk=pk).values("interface_name", "body", "interface_path", "method").first()
        case_steps = models.CaseSuitInfo.objects.filter(source_api_id=pk)
        case_steps.update(**source_api, updater=request.user.username, update_time=datetime.datetime.now())
        case_ids = case_steps.values('case')
        models.CaseSuit.objects.filter(pk__in=case_ids).update(update_time=datetime.datetime.now(),
                                                           updater=request.user.username)
        return Response(response.CASE_STEP_SYNC_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def single(self, request, **kwargs):
        """
        api-获取单个api详情，返回body信息

        获取单个api的详细情况
        """
        try:
            api = models.API.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        parse = Parse(eval(api.body))
        parse.parse_http()

        resp = {
            'id': api.id,
            'body': parse.testcase,
            'success': True,
            'creator': api.creator,
            'relation': api.relation,
            'project': api.project.id,
        }

        return Response(resp)
