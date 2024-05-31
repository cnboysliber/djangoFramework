import json
from django.utils import timezone

from loguru import logger

from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser

from FasterRunner import pagination
from FasterRunner import const as cnt
from performApp import models
from performApp import serializers
from performApp.utils import response
from FasterRunner.utils.decorator import request_log


class TestTypeView(GenericViewSet):
    """
    testtype-测试类型增删改查
    """
    queryset = models.TestType.objects
    serializer_class = serializers.TestTypeSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def query(self, request):
        """
        testtype-查询类型列表

        :param request:
        :return:
        """
        filters = dict({})
        filters['name__contains'] = request.query_params.get('name', '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-update_time')
        if request.query_params != {}:
            queryset = queryset.filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        testtype-查询测试类型详情

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
        testtype-添加测试类型

        :param request:
        :return:
        """
        context = {
            "request": self.request,
        }
        # 反序列化
        serializer = self.serializer_class(data=request.data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(response.TYPE_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        testtype-单个删除测试类型记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            if models.ScenesManage.objects.filter(test_type=kwargs['pk']).first():
                return Response(response.TYPE_DELETE_ERROR)
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE,
                                                         updater=request.user.username, update_time=timezone.now())
            return Response(response.TYPE_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request, **kwargs):
        """
        testtype-批量删除测试类型记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))).update(status=cnt.NOT_ACTIVE, updater=request.user.username, update_time=timezone.now())
            return Response(response.TYPE_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        testtype-更新测试类型

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw, updater=request.user.username, update_time=timezone.now())
            return Response(response.TYPE_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)