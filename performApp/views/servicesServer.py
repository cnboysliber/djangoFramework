# -*- coding: utf-8 -*-
from loguru import logger

from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser

from FasterRunner import pagination
from FasterRunner import const as cnt
from FasterRunner.utils.decorator import request_log
from performApp import models
from performApp import serializers
from performApp.utils import response


class ServicesServerView(GenericViewSet):
    """
    ServicesServer-性能环境增删改查
    """
    queryset = models.ServicesServer.objects
    serializer_class = serializers.ServicesServerSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        ServicesServer-查询列表

        :param request:
        :return:
        """

        filters = dict({})
        filters['env_id'] = request.query_params.get('env_id')
        filters['server_ip__contains'] = request.query_params.get("server_ip", '')
        filters['server_type__in'] = request.query_params.get("server_type", '') or [1, 2, 3, 4, 5]

        keyword = request.query_params.get("keyword", '')
        q = self.queryset.filter(status=cnt.ACTIVE).order_by('-create_time')

        if request.query_params != '':
            q = q.filter(Q(server_ip__contains=keyword))\
                .filter(**filters)

        pagination_queryset = self.paginate_queryset(q)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def get_detail(self, request, **kwargs):
        """
        ServicesServer-查询详情

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
        ServicesServer-添加性能项目

        :param request:
        :return:
        """
        # 反序列化
        context = {
            "request": self.request,
        }
        serializer = self.serializer_class(data=request.data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(response.ENV_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        ServicesServer-单个删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.ENV_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request):
        """
        ServicesServer-批量删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.ENV_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        ServicesServer-更新

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            return Response(response.ENV_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)






