# -*- coding: utf-8 -*-
import json

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from FasterRunner import pagination
from FasterRunner import const as cnt
from performApp import models
from performApp import serializers
from performApp.utils import response
from FasterRunner.utils.logging import logger
from performApp.utils.jacocoExecute import async_run_jacoco, batch_execute
from FasterRunner.utils.decorator import request_log


class CoverageServiceView(GenericViewSet):
    """
    coverage-Jacoco服务类接口视图
    """
    queryset = models.JacocoService.objects
    serializer_class = serializers.JacocoServiceSerializer
    pagination_class = pagination.MyPageNumberPagination

    @method_decorator(request_log(level='INFO'))
    def list(self, request):
        """
        coverage-查询服务列表

        :param request:
        :return:
        """
        filters = dict({})
        filters['service_name__contains'] = request.query_params.get('service_name', '')
        filters['module__contains'] = request.query_params.get("module", '')

        keyword = request.query_params.get("keyword", '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-create_time')
        if request.query_params != '':
            queryset = queryset.filter(Q(service_name__contains=keyword) |
                                       Q(module__contains=keyword)) \
                .filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def get_detail(self, request, **kwargs):
        """
        perform-查询报告详情

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
        coverage-服务添加

        :param request:
        :return:
        """

        # 反序列化
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(response.PERFORM_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        coverage-删除服务列表

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request, **kwargs):
        """
        coverage-批量服务

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        coverage-更新服务信息

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            return Response(response.PERFORM_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)


class CoverageTaskView(GenericViewSet):
    """
    coverage-Jacoco服务类接口视图
    """
    queryset = models.JacocoTask.objects
    serializer_class = serializers.JacocoTaskSerializer
    pagination_class = pagination.MyPageNumberPagination

    @method_decorator(request_log(level='DEBUG'))
    def log(self, request):
        """
        coverage-查询运行日志详情

        :param request:
        :return:
        """
        filters = dict({})
        filters['service_id'] = request.query_params.get('serviceId', '')

        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-reqTime', 'reqPeriod')
        queryset = queryset.filter(**filters)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def run_single(self, request):
        """
        coverage-运行jacoco任务

        :param request:
        :return:
        """
        service_id = request.data.get('service_id')
        try:
            async_run_jacoco(service_id)
        except Exception as e:
            logger.error(e)
            return Response(response.COVERAGE_RUN_ERROR)
        resp_data = response.COVERAGE_RUN_SUCCESS
        return Response(resp_data)

    @method_decorator(request_log(level='INFO'))
    def batch_run(self, request):
        """
        coverage-运行jacoco任务

        :param request:
        :return:
        """
        service_ids = json.loads(request.data.get('service_ids'))
        try:
            batch_execute(service_ids)
        except Exception as e:
            logger.error(e)
            return Response(response.COVERAGE_RUN_ERROR)
        resp_data = response.COVERAGE_RUN_SUCCESS
        return Response(resp_data)

    def view_log(self, request):
        """
        coverage-查看覆盖率日志文件
        :param request:
        :return:最后一条日志解码数据
        """
        service_id = request.query_params.get('service_id')
        queryset = self.queryset.filter(status=cnt.ACTIVE, service_id=service_id).order_by('-create_time')
        queryset = queryset.first()
        serializer = self.get_serializer(queryset)
        data = serializer.data
        data['log'] = json.loads(serializer.data['log']) if data['log'] else data['log']
        return Response(data)
