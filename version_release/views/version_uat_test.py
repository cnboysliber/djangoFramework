# -*- coding: utf-8 -*-
import os
import xlrd
import shutil
from xlrd import xldate_as_tuple
from datetime import datetime
from loguru import logger

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


class VersionUATView(GenericViewSet):
    """
    uat版本提测增删改查
    """
    queryset = models.VersionUATManage.objects.all()
    serializer_class = serializers.VersionUATManageSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        uat查询提测列表

        :param request:
        :return:
        """
        keyword = request.query_params.get("keyword", '')
        if keyword != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(status=cnt.ACTIVE)
            projects_fileter = projects_fileters.filter(Q(product_line__contains=keyword) |
                                                        Q(project_name__contains=keyword) |
                                                        Q(assembly_name__contains=keyword) |
                                                        Q(develop_man__contains=keyword) |
                                                        Q(test_man__contains=keyword) |
                                                        Q(business_line__contains=keyword))

        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(status=cnt.ACTIVE)
        pagination_queryset = self.paginate_queryset(projects_fileter)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        uat-查询提测详情

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
        uat-添加提测（暂时未用）

        :param request:
        :return:
        """

        # 反序列化
        serializer = serializers.VersionUATManageSerializer(data=request.data)

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
        uat-单个删除提测记录

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
        uat-批量删除提测记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.PERFORM_AUTH_PERMISSIONS)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        uat-更新性能报告

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
    def upload_excel(self, request):
        """
        uat-性能报告导入（暂时未用）

        :param request:
        :return:
        """
        file = request.FILES['file']
        if not (file.name.endswith('.xls') or file.name.endswith('.xlsx')):
            return Response(response.PERFORM_TYPE_ERROR)
        content = file.read()
        wb = xlrd.open_workbook(file_contents=content)
        sht = wb.sheet_by_index(0)
        headers = cnt.UPLOAD_HEAD
        for row in range(1, sht.nrows):
            perform_data = {}
            cells = sht.row_values(row)
            for index, value in enumerate(cells):
                if index < 4 or len(cells) - index < 3:
                    perform_data[headers[index]] = value or sht.row_values(row - 1)[index]
                else:
                    perform_data[headers[index]] = value.strip() if isinstance(value, str) else value
                if headers[index] in ['apiIndex', 'reqCount', 'respMs']:
                    perform_data[headers[index]] = int(value)
                elif headers[index] == 'errRate':
                    perform_data[headers[index]] = int(float(value * 10000))
                elif headers[index] == 'tps':
                    perform_data[headers[index]] = int(float(value * 100))

                elif headers[index] == 'reqTime':
                    if value:
                        perform_data[headers[index]] = datetime(*xldate_as_tuple(value, 0)).strftime('%Y-%m-%d')
                    else:
                        perform_data[headers[index]] = datetime(*xldate_as_tuple(sht.row_values(row - 1)[index]
                                                                                 , 0)).strftime('%Y-%m-%d')
                if index == 1:
                    value = 1 if (value or sht.row_values(row - 1)[index].strip()) == 'B端' else 2

                    perform_data[headers[index]] = value
            serializer = serializers.VersionUATManageSerializer(data=perform_data)

            if serializer.is_valid():
                serializer.save()
            else:
                logger.error(serializer.errors)
        return Response(response.PERFORM_UPLOAD_SUCCESS)





