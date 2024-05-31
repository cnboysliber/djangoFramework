# -*- coding: utf-8 -*-
import os
import xlrd
import shutil
import json
from xlrd import xldate_as_tuple
from datetime import datetime
from loguru import logger
from rest_framework import generics
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import OrderingFilter
from FasterRunner import pagination
from FasterRunner import const as cnt
from FasterRunner.utils.decorator import request_log
from version_release import models
from version_release import serializers
from version_release.utils import response


class PerformView(GenericViewSet):
    """
    服务增删改查
    """
    queryset = models.SeviceListTable.objects.all()
    serializer_class = serializers.SeviceListTableModelSerializer
    pagination_class = pagination.MyPageNumberPagination
    # filter_backends=[OrderingFilter]
    parser_classes = [MultiPartParser, FormParser]

    # ordering_fields = ['create_time']

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        查询服务列表

        :param request:
        :return:
        """
        filter_columns = ['business_line', 'product_line', 'function_name',
                          'project_name', 'assembly_name', 'develop_man', 'test_man']
        filters = {'%s__contains' % k: v for k, v in request.query_params.items()
                   if v and k in filter_columns}
        keyword = request.query_params.get("keyword", '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-id')
        if request.query_params != '':
            queryset = queryset.filter(Q(product_line__contains=keyword) |
                                       Q(project_name__contains=keyword) |
                                       Q(assembly_name__contains=keyword) |
                                       Q(develop_man__contains=keyword) |
                                       Q(test_man__contains=keyword) |
                                       Q(business_line__contains=keyword) |
                                       Q(product_line__contains=keyword)) \
                .filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        perform-查询服务详情

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        queryset = self.queryset.filter(id=pk, status=cnt.ACTIVE).first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def get_service_detail(self, request, **kwargs):
        """
        perform-查询服务详情

        :param request:
        :return:
        """
        project_name = kwargs.get('pk')
        queryset = self.queryset.filter(project_name=project_name, status=cnt.ACTIVE).first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        -添加服务

        :param request:
        :return:
        """

        # 反序列化
        serializer = serializers.SeviceListTableModelSerializer(data=request.data)
        if serializer.is_valid():
            if {'project_name':request.data['project_name']} in models.SeviceListTable.objects.values('project_name'):
                return Response(response.PROJECT_EXISTS_SUCCESS)
            else:
                serializer.save()
                return Response(response.PERFORM_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        perform-单个删除服务记录

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
        perform-批量删除报告记录

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
        perform-更新服务详情

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
    def business_list(self, request, **kwargs):
        """
        获取业务线列表

        :param request:
        :return:
        """
        business_name=models.SeviceListTable.objects.values('business_line').distinct()
        business_name = business_name.filter(status=cnt.ACTIVE).exclude(business_line='').exclude(business_line=None)
        return Response(business_name)

    @method_decorator(request_log(level='INFO'))
    def product_list(self, request, **kwargs):
        """
        获取产品线列表

        :param request:
        :return:
        """
        product_line=models.SeviceListTable.objects.values('product_line').distinct()
        product_line = product_line.filter(status=cnt.ACTIVE).exclude(product_line='').exclude(product_line=None)
        return Response(product_line)

    @method_decorator(request_log(level='INFO'))
    def function_list(self, request, **kwargs):
        """
        获取功能名称列表

        :param request:
        :return:
        """
        function_name = models.SeviceListTable.objects.values('function_name').distinct()
        function_name = function_name.filter(status=cnt.ACTIVE).exclude(function_name='').exclude(function_name=None)
        return Response(function_name)

    @method_decorator(request_log(level='INFO'))
    def project_list(self, request, **kwargs):
        """
        获取工程名称列表

        :param request:
        :return:
        """
        project_name = models.SeviceListTable.objects.values('project_name').distinct()
        project_name = project_name.filter(status=cnt.ACTIVE).exclude(project_name='').exclude(project_name=None)
        return Response(project_name)

    @method_decorator(request_log(level='INFO'))
    def assembly_list(self, request, **kwargs):
        """
        获取组件列表

        :param request:
        :return:
        """
        assembly_name = models.SeviceListTable.objects.values('assembly_name').distinct()
        assembly_name = assembly_name.filter(status=cnt.ACTIVE).exclude(assembly_name='').exclude(assembly_name=None)
        return Response(assembly_name)

    @method_decorator(request_log(level='INFO'))
    def develop_list(self, request, **kwargs):
        """
        获取开发维护人列表

        :param request:
        :return:
        """
        develop_man = models.SeviceListTable.objects.values('develop_man').distinct()
        develop_man = develop_man.filter(status=cnt.ACTIVE).exclude(develop_man ='').exclude(develop_man=None)
        return Response(develop_man)

    @method_decorator(request_log(level='INFO'))
    def test_list(self, request, **kwargs):
        """
        获取测试维护人列表

        :param request:
        :return:
        """
        test_man = models.SeviceListTable.objects.values('test_man').distinct()
        test_man = test_man.filter(status=cnt.ACTIVE).exclude(test_man ='').exclude(test_man=None)
        return Response(test_man)

    def get_proAssembly_name(self,request,**kwargs):
        '''
        获取所有的工程组件名
        '''

        pk_1 = request.query_params.get("pro_data",'')#得到前端传的产品名称
        pk_2 = request.query_params.get("ass_data",'') # 得到前端传的业务名称
        queryset = self.queryset.filter(status=cnt.ACTIVE)
        queryset.filter(business_line=pk_2).filter(product_line=pk_1).distinct()
        pro_name = queryset.values('project_name')
        assembly_name = queryset.values('assembly_name')
        project_name_data = []
        for i in range(len(assembly_name)):
            project_list=str(str(assembly_name[i]['assembly_name'])+'/'+str(pro_name[i]['project_name']))
            project_name_data.append({"key":str(i+1),"label":project_list})
        return Response(project_name_data)

    def get_project_data(self,request,**kwargs):
        '''
        获取所有的工程组件名
        '''
        pk= request.query_params.get("pro_ass_id")#得到前端传id
        ass_name=pk.split('/')[1]
        queryset = self.queryset.filter(status=cnt.ACTIVE).filter(project_name__contains=ass_name).first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def get_proAssembly__line(self,request,**kwargs):
        '''
        选择产品业务线后获取组件与工程名
        '''

        pk_1 = request.query_params.get("pro_data")#得到前端传的产品名称
        pk_2 = request.query_params.get("ass_data")
        queryset = self.queryset.filter(status=cnt.ACTIVE)
        queryset = queryset.filter(business_line=pk_2).filter(product_line=pk_1)
        pro_name = queryset.values('project_name')
        assembly_name = queryset.values('assembly_name')
        project_name_data = []
        for i in range(len(assembly_name)):
            project_list=str(str(assembly_name[i]['assembly_name'])+'/'+str(pro_name[i]['project_name']))
            project_name_data.append({"key":str(i+1),"label":project_list})
        return Response(project_name_data)
