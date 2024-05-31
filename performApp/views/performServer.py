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
from FasterRunner.utils.decorator import request_log
from performApp import models
from performApp import serializers
from performApp.utils import response
from performApp.utils.jmeterApi import JmRest


class PerformServerView(GenericViewSet):
    """
    performServer-压力机信息增删改查
    """
    queryset = models.PerformServer.objects
    serializer_class = serializers.PerformServerSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def query(self, request):
        """
        performServer-压力机列表

        :param request:
        :return:
        """
        filters = dict({})
        filters['srv_type__in'] = request.query_params.get('srv_type') or [0, 1]
        filters['used__in'] = request.query_params.get('used') or [0, 1]
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-create_time')
        if request.query_params != {}:
            queryset = queryset.filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        performServer-查询压力机详情

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
        performServer-添加压力机

        :param request:
        :return:
        """
        # QueryDict对象添加用户信息
        # request = serializers.PerformServerSerializer.get_user_info(request)
        request = serializers.PerformServerSerializer.get_update_info(request)
        # 反序列化
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(response.PERFORM_SERVER_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        performServer-单个删除压力机记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE, updater=request.user.username, update_time=timezone.now())
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request, **kwargs):
        """
        performServer-批量删除压力机记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))).update(status=cnt.NOT_ACTIVE, updater=request.user.username, update_time=timezone.now())
            return Response(response.PERFORM_SERVER_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        performServer-更新压力机

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw, updater=request.user.username, update_time=timezone.now())
            return Response(response.PERFORM_SERVER_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)


class JmeterWorkView(GenericViewSet):
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log('DEBUG'))
    def get_work_list(self, request):
        """
        查询执行机详情
        :param request:
        :return:
        """
        state = request.query_params.get('state', 'all')
        page_size = int(request.query_params.get('pageSize', 2))
        page_number = int(request.query_params.get('pageNumber', 1))
        jmt = JmRest()
        work_list = jmt.get_work_list()
        if state != 'all':
            work_list = list(filter(lambda x: x['state'] == state, work_list))

        count = len(work_list)
        if (count + 1) // page_size + 1 < int(page_number):
            page_number = (count + 1) // page_size + 1
            work_list = work_list[-page_number:]
        else:
            step = (page_number - 1) * page_size
            work_list = work_list[step: page_size + step]
        result = {
            'code': '000000',
            'msg': '查询成功',
            'data': work_list,
            'count': count
        }
        return Response(result)

    @method_decorator(request_log('DEBUG'))
    def action_worker(self, request):
        """
        worker节点上下线
        :param request:
        :return:
        """
        action = request.data.get('action')
        worker_host = request.data.get('host')
        jmt = JmRest()
        jmt.work_action(worker_host, action)
        result = response.WORKER_RESTART_SUCCESS if action == 'restart' else response.WORKER_STOP_SUCCESS
        return Response(result)


