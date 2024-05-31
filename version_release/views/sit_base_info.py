# -*- coding: utf-8 -*-
from loguru import logger
from django.db.models import Count
from django.db.models import Q
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


class BaseRaiseInfoView(GenericViewSet):
    """
    版本提测增删改查
    """
    queryset = models.BaseRaiseInfo.objects.all()
    serializer_class = serializers.BaseRaiseInfoSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        查询服务列表

        :param request:
        :return:
        """
        keyword = request.query_params.get("keyword", '')
        if keyword != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(status=cnt.ACTIVE).order_by('-id')
            projects_fileter = projects_fileters.filter(Q(system_name__contains=keyword) |
                                                        Q(raise_version__contains=keyword) |
                                                        Q(raise_time__contains=keyword) |
                                                        Q(raise_label__contains=keyword) |
                                                        Q(pro_name__contains=keyword) |
                                                        Q(project_label__contains=keyword) |
                                                        Q(raise_env__contains=keyword) |
                                                        Q(raise_people__contains=keyword) |
                                                        Q(level__contains=keyword) |
                                                        Q(program_status__contains=keyword))

        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(status=cnt.ACTIVE).order_by('-id')
        pagination_queryset = self.paginate_queryset(projects_fileter)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        查询基础提测详情

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        queryset = self.queryset.filter(id=pk, status=cnt.ACTIVE).first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        更新基础提测信息

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
    def CheckModify(self, request, **kwargs):
        """
        审核更新基础提测信息

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            if request.data['checkResults'] == '通过':
                self.queryset.filter(id=pk).update(program_status='审核通过')
            else:
                self.queryset.filter(id=pk).update(program_status='审核不通过')
            return Response(response.PERFORM_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def RaiseModify(self, request, **kwargs):
        """
        审核更新基础提测信息

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            self.queryset.filter(id=pk).update(program_status='已发布uat')
            # self.queryset.filter(id=pk).update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        添加基础提测信息

        :param request:
        :return:
        """

        # 反序列化
        serializer = serializers.BaseRaiseInfoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            rest = response.PERFORM_ADD_SUCCESS
            rest['id'] = serializer.data['id']
            return Response(rest)
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
        if self.queryset.filter(id=kwargs['pk']).values('program_status') == '审核通过':
            if request.user.is_superuser is False:
                return Response(response.PERFORM_AUTH_PERMISSIONS)
            try:
                self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
                return Response(response.PERFORM_DELETE_SUCCESS)
            except ObjectDoesNotExist:
                return Response(response.SYSTEM_ERROR)
        else:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
