from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from FasterRunner import pagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import GenericViewSet
from loguru import logger
from FasterRunner import const as cnt
from FasterRunner.utils.decorator import request_log
from quality_management import models, serializers
from quality_management.utils import response


class MonthVersionApiView(GenericViewSet):
    """
    月版本增删改查
    """
    queryset = models.MonthVersion.objects.all()
    serializer_class = serializers.MonthVersionSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def add(self, request):
        """
        MonthVersion-添加月版本
        :param request:
        :return:
        """
        is_exist = self.queryset.filter(status=cnt.ACTIVE, year_month=request.data['year_month']).first()
        context = {
            "request": serializers.MonthVersionSerializer.get_login_info(request),
        }
        # 反序列化
        serializer = self.serializer_class(data=request.data, context=context)
        if is_exist is None:
            if serializer.is_valid():
                serializer.save()
                return Response(response.MONTH_VERSION_ADD_SUCCESS)
            logger.error(serializer.errors)
            ret = response.SYSTEM_ERROR
            ret.update({'msg': serializer.errors})
            return Response(ret)
        else:
            return Response(response.MONTH_VERSION_TIP_SUCCESS)

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        MonthVersion-查询月版本
        :param request:
        :return:
        """
        # filters = dict({})
        # filters['name__contains'] = request.query_params.get('name', '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-update_time')
        # if request.query_params != {}:
        #     queryset = queryset.filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def modify(self, request, **kwargs):
        """
        MonthVersion-修改月版本
        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            return Response(response.MONTH_VERSION_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        MonthVersion-单个删除月版本

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.VERSION_AUTH_PERMISSIONS)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.MONTH_VERSION_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)


class VersionApiView(GenericViewSet):
    """
    版本增删改查
    """
    queryset = models.Version.objects.all()
    serializer_class = serializers.VersionSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def add(self, request):
        """
        Version-添加版本
        :param request:
        :return:
        """
        context = {
            "request": serializers.VersionSerializer.get_login_info(request),
        }
        # 反序列化
        serializer = self.serializer_class(data=request.data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(response.VERSION_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        Version-查询版本
        :param request:
        :return:
        """
        # filters = dict({})
        # filters['name__contains'] = request.query_params.get('name', '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-update_time')
        # if request.query_params != {}:
        #     queryset = queryset.filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def modify(self, request, **kwargs):
        """
        Version-修改版本
        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            return Response(response.VERSION_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        Version-单个删除版本

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.VERSION_AUTH_PERMISSIONS)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.VERSION_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request, **kwargs):
        """
        Version-批量删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.VERSION_AUTH_PERMISSIONS)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.VERSION_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)


class ChildVersionApiView(GenericViewSet):
    """
    子版本增删改查
    """
    queryset = models.ChildVersion.objects.all()
    serializer_class = serializers.ChildVersionSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def add(self, request):
        """
        ChildVersion-添加子版本
        :param request:
        :return:
        """
        context = {
            "request": serializers.ChildVersionSerializer.get_login_info(request),
        }
        # 反序列化
        serializer = self.serializer_class(data=request.data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(response.CHILD_VERSION_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        ChildVersion-查询子版本
        :param request:
        :return:
        """
        # filters = dict({})
        # filters['name__contains'] = request.query_params.get('name', '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-update_time')
        # if request.query_params != {}:
        #     queryset = queryset.filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def modify(self, request, **kwargs):
        """
        ChildVersion-修改子版本
        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            return Response(response.CHILD_VERSION_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        ChildVersion-单个删除子版本

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.VERSION_AUTH_PERMISSIONS)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.CHILD_VERSION_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request, **kwargs):
        """
        ChildVersion-批量删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.VERSION_AUTH_PERMISSIONS)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.CHILD_VERSION_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)


class AllVersionApiView(GenericViewSet):
    """
    所有版本增删改查
    """
    queryset_child = models.ChildVersion.objects.all()
    queryset_version = models.Version.objects.all()
    queryset_month = models.MonthVersion.objects.all()
    serializer_class = serializers.MonthVersionSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        ChildVersion-查询子版本
        :param request:
        :return:
        """
        filters = dict({})
        filters['year_month__contains'] = request.query_params.get('year_month', '')
        queryset_month = self.queryset_month.filter(status=cnt.ACTIVE, type=1).order_by('-update_time')
        if request.query_params != {}:
            queryset_month = self.queryset_month.filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset_month)
        serializer = self.get_serializer(pagination_queryset, many=True)
        queryset_month = serializer.data
        version_list = []
        if queryset_month is not []:
            for item_month in queryset_month:
                queryset_version = self.queryset_version.filter(status=cnt.ACTIVE, month_version_id=item_month['id']).\
                    values('id', 'name').order_by('-update_time')
                if queryset_version.count() != 0:
                    for item_version in queryset_version:
                        queryset_child = self.queryset_child.filter(status=cnt.ACTIVE, version_id=item_version['id']).\
                            values('system_name', 'version_num').order_by('-update_time')
                        if queryset_child.count() != 0:
                            for item_child in queryset_child:
                                version_list.append({'year_month': item_month['year_month'],
                                                     'name': item_version['name'],
                                                     'system_name': item_child['system_name'],
                                                     'version_num': item_child['version_num']})
                        else:
                            version_list.append({'year_month': item_month['year_month'],
                                                 'name': item_version['name']})
                else:
                    version_list.append({'year_month': item_month['year_month']})
        else:
            version_list = []

        return Response({'count': len(version_list), 'msg': 'success', 'results': version_list})
