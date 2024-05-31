# -*- coding: utf-8 -*-
import os, datetime, time, xlrd
import json
import traceback
from loguru import logger
from xlrd import xldate_as_tuple
from django.db.models import Count
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from FasterRunner import pagination
from FasterRunner import const as cnt
from quality_management import models
from quality_management import serializers
from quality_management.utils import response
from FasterRunner.utils.decorator import request_log


class OrganizationApiView(GenericViewSet):
    """
    组织架构文件上传
    """
    queryset = models.UploadOrganizationData.objects.all()
    serializer_class = serializers.UploadOrganizationDataSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        组织架构列表

        :param request:
        :return:
        """
        keyword = request.query_params.get("keyword", '')
        if keyword != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(status=cnt.ACTIVE)
            projects_fileter = projects_fileters.filter(upload_time__contains=keyword[:7])

        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(status=cnt.ACTIVE)
            upload_time = models.UploadOrganizationData.objects.values('upload_time').distinct().order_by('-upload_time').first()
            projects_fileter = projects_fileter.filter(upload_time=upload_time['upload_time'])
        pagination_queryset = self.paginate_queryset(projects_fileter)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        uat-单个删除提测记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.ORGANIZATION_AUTH_PERMISSIONS)
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
            return Response(response.ORGANIZATION_AUTH_PERMISSIONS)
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
            return Response(response.ORGANIZATION_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def upload_file(self, request):
        """
        ScriptParams-脚本文件上传

        :param request:
        :return:
        """
        # 反序列化
        resp = response.PERFORM_UPLOAD_SUCCESS
        file = request.FILES['file']
        if not (file.name.endswith('.xls') or file.name.endswith('.xlsx')):
            return Response(response.ORGANIZATION_TYPE_ERROR)
        content = file.read()
        wb = xlrd.open_workbook(file_contents=content)
        sht = wb.sheet_by_index(0)
        headers = ['name', 'job', 'business_line', 'develop_group', 'person_type', 'workspace', 'skill_name',
                   'person_state']
        headers = headers[: len(sht.row_values(0))]
        perform_data = dict({})
        model_data = []
        for row in range(1, sht.nrows):
            cells = sht.row_values(row)
            cells.pop(0)
            for index, value in enumerate(cells):
                perform_data[headers[index]] = value
            model_data.append(models.UploadOrganizationData(**perform_data))
        try:
            models.UploadOrganizationData.objects.bulk_create(model_data)
        except Exception as e:
            logger.error('插入数据异常：{}'.format(str(e)))
            logger.error(traceback.format_exc())
            resp = response.ORGANIZATION_UPLOAD_ERROR
            resp['msg'] = str(e)
            return Response(resp)
        return Response(resp)

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        -添加服务

        :param request:
        :return:
        """
        request.POST._mutable = True
        upload_time = models.UploadOrganizationData.objects.values('upload_time').distinct().order_by(
            '-upload_time').first()
        request.data['upload_time']=upload_time["upload_time"]
        #反序列化
        serializer = serializers.UploadOrganizationDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(response.ORGANIZATION_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)