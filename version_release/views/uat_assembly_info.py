# -*- coding: utf-8 -*-
import os
import xlrd
import shutil
from xlrd import xldate_as_tuple
from datetime import datetime
from loguru import logger
from django.db.models import Count
from version_release.utils import day

from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser

from FasterRunner import pagination
from FasterRunner import const as cnt
from version_release import models
from version_release import serializers
from version_release.utils import response
from FasterRunner.utils.decorator import request_log


class UatAssemblyInfoView(GenericViewSet):
    """
    版本提测增删改查
    """
    queryset = models.UatAssemblyList.objects.all()
    serializer_class = serializers.UatAssemblyListSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        查询提测列表

        :param request:
        :return:
        """

        keyword = request.query_params.get("keyword", '')
        if keyword != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(status=cnt.ACTIVE).order_by('-id')
            projects_fileter = projects_fileters.filter(Q(product_line__contains=keyword) |
                                                        Q(system_name__contains=keyword) |
                                                        Q(pro_name__contains=keyword) |
                                                        Q(raise_people__contains=keyword) |
                                                        Q(level__contains=keyword) |
                                                        Q(raise_env__contains=keyword) |
                                                        Q(raise_time__contains=keyword) |
                                                        Q(business_line__contains=keyword)
                                                        )

        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(status=cnt.ACTIVE).order_by('-id')
        pagination_queryset = self.paginate_queryset(projects_fileter)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        perform-查询提测详情

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        queryset = self.queryset.filter(project=pk, status=cnt.ACTIVE)
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        uat-更新提测信息

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

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        perform-添加提测任务

        :param request:
        :return:
        """

        # 反序列化
        serializer = serializers.UatAssemblyListSerializer(data=request.data)

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
        perform-单个删除提测记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.PERFORM_AUTH_PERMISSIONS)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request, **kwargs):
        """
        perform-批量删除提测记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.PERFORM_AUTH_PERMISSIONS)
        try:
            self.queryset.filter(id_in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    def data_list(self,request):
        #统计每天提测个数
        count_data = self.get_queryset() \
            .filter(status=cnt.ACTIVE) \
            .extra(select={"apply_time": "DATE_FORMAT(apply_time,'%%m-%%d')"}) \
            .values('apply_time') \
            .annotate(counts=Count('id')).values('apply_time', 'counts')

        apply_time = []
        count = []
        for d in count_data:
            apply_time.append(d['apply_time'])
            count.append(d['counts'])
        return Response({'apply_time': apply_time, 'count': count})

    #各环境发布数
    def program_status_list(self,request):

        count_data = self.get_queryset() \
            .filter(status=cnt.ACTIVE) \
            .extra(select={"program_status":'program_status'}) \
            .values('program_status') \
            .annotate(counts=Count('id')).values('program_status', 'counts')

        program_status = []
        count_msg = []
        for d in count_data:
            program_status.append(d['program_status'])
            count_msg.append(d['counts'])
        return Response({'program_status': program_status, 'count_msg': count_msg})
