# -*- coding: utf-8 -*-
from loguru import logger

from django.db.models import Q
from django.db.transaction import Atomic
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
from performApp.utils import error as err
from performApp.utils import response
from FasterRunner.utils.decorator import request_log


class PerformProjectView(GenericViewSet):
    """
    perform-性能报告增删改查
    """
    queryset = models.PerformProject.objects
    serializer_class = serializers.PerformProjectSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        perform-查询列表

        :param request:
        :return:
        """

        filters = dict({})
        filters['ptype__in'] = request.query_params.get('ptype') or [1, 2]
        filters['run_status__in'] = request.query_params.get('run_status') or [0, 1, 2]
        filters['project__contains'] = request.query_params.get('project', '')
        filters['dev_manager__contains'] = request.query_params.get("dev_manager", '')
        filters['developer__contains'] = request.query_params.get("developer", '')
        filters['tester__contains'] = request.query_params.get("tester", '')

        keyword = request.query_params.get("keyword", '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-create_time')

        if request.query_params != '':
            queryset = queryset.filter(Q(project__contains=keyword) |
                                       Q(dev_manager__contains=keyword) |
                                       Q(developer__contains=keyword) |
                                       Q(tester__contains=keyword))\
                .filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        perform-查询详情

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
        perform-添加性能项目

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
            return Response(response.PROJECT_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        perform-单个删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.UNAUTHORIZED_ERROR)
        try:
            if models.ScenesManage.objects.filter(project_id=kwargs['pk'], status=cnt.ACTIVE).first():
                raise err.AppError(500, '该项目下还有场景未删除，请先删除场景')
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.PROJECT_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request):
        """
        perform-批量删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.UNAUTHORIZED_ERROR)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.PROJECT_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        perform-更新

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            try:
                update_kw['err_rate'] = int(update_kw['err_rate'])
            except Exception as e:
                logger.error(str(e))
                raise Exception('错误率格式不对')
            self.queryset.filter(id=pk).update(**update_kw)
            return Response(response.PROJECT_UPDATE_SUCCESS)

        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

        except Exception as e:
            print(e)
            error = {k: v for k, v in response.SYSTEM_ERROR}
            error.update({'message': e})
            return Response(error)




