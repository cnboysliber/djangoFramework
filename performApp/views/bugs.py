# -*- coding: utf-8 -*-
import os
import tempfile
import time

import requests
from django.http import HttpResponse, FileResponse
from django.utils.encoding import escape_uri_path
from loguru import logger
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
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


class BugsView(GenericViewSet):
    """
    Bugs-Bugs增删改查
    """
    queryset = models.Bugs.objects
    serializer_class = serializers.BugsSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        Bugs-查询列表

        :param request:
        :return:
        """
        filters = dict({})
        project_id = request.query_params.get('project_id', '')
        filters['api_url__contains'] = request.query_params.get("api_url", '')
        filters['state__in'] = request.query_params.get("state") or [1, 2, 3, 4]
        filters['bug_severity__in'] = request.query_params.get("bug_severity") or [1, 2, 3, 4, 5]
        if project_id:
            filters['project_id'] = project_id

        keyword = request.query_params.get("keyword", '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-create_time')

        if request.query_params != {}:
            queryset = queryset.filter(Q(bug_severity__in=keyword) |
                                       Q(api_url__contains=keyword) |
                                       Q(state__in=keyword))\
                .filter(**filters)

        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def get_detail(self, request, **kwargs):
        """
        Bugs-查询详情

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        queryset = self.queryset.filter(id=pk, status=cnt.ACTIVE).first()
        serializer = self.get_serializer(queryset)
        res = serializer.data
        one_img_list, two_img_list = [], []
        if res['field_img_one']:
            temp_list = res['field_img_one'].split(',')
            for img in temp_list:
                one_img_dict = {'name': img, 'url': os.path.join(settings.IMAGES_DIR, img)}
                one_img_list.append(one_img_dict)
            res['field_img_one'] = one_img_list
        else:
            res['field_img_one'] = []
        if res['field_img_two'] and res['field_img_two'] != '':
            temp_list = res['field_img_two'].split(',')
            for img in temp_list:
                two_img_dict = {'name': img, 'url': os.path.join(settings.IMAGES_DIR, img)}
                two_img_list.append(two_img_dict)
            res['field_img_two'] = two_img_list
        else:
            res['field_img_two'] = []
        return Response(res)

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        Bugs-添加bugs

        :param request:
        :return:
        """
        # 序列化
        context = {
            "request": serializers.BugsSerializer.get_update_info(request),
        }
        # 加载文件id
        file_one_id_list, file_two_id_list = [], []
        file_one = request.FILES.getlist('field_img_one')
        file_two = request.FILES.getlist('field_img_two')
        # 上传图片且装换为图片名称
        if not os.path.exists(settings.IMAGES_DIR):
            os.mkdir(settings.IMAGES_DIR)
        if file_one:
            for k, v in dict(request.data).items():
                if k == 'field_img_one':
                    for i in v:
                        filename = f"{i.name.split('.')[0]}_{int(round(time.time() * 1000000))}.{i.name.split('.')[-1]}"
                        file_one_id_list.append(filename)
                        i.name = filename
                        with open(os.path.join(settings.IMAGES_DIR, filename), 'wb+') as fp:
                            for chunk in i.chunks():
                                fp.write(chunk)
                    request.data[k] = ','.join(file_one_id_list)
        if file_two:
            for k, v in dict(request.data).items():
                if k == 'field_img_two':
                    for i in v:
                        filename = f"{i.name.split('.')[0]}_{int(round(time.time() * 1000000))}.{i.name.split('.')[-1]}"
                        file_two_id_list.append(filename)
                        i.name = filename
                        with open(os.path.join(settings.IMAGES_DIR, filename), 'wb+') as fp:
                            for chunk in i.chunks():
                                fp.write(chunk)
                    request.data[k] = ','.join(file_two_id_list)

        serializer = self.serializer_class(data=request.data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(response.BUGS_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        Bugs-单个删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE, updater=request.user.username, update_time=timezone.now())
            return Response(response.BUGS_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request):
        """
        Bugs-批量删除

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE, updater=request.user.username, update_time=timezone.now())
            return Response(response.BUGS_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        Bugs-更新

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            if request.FILES.getlist('field_img_one') or request.FILES.getlist('field_img_two'):
                update_temp = {k: v for k, v in dict(request.data).items()}
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            file_one_id_list, file_two_id_list = [], []
            for k in update_kw.keys():
                if k == 'field_img_one':
                    update_kw[k] = update_temp['field_img_one']
                    for i in update_kw[k]:
                        filename = f"{i.name.split('.')[0]}_{int(round(time.time() * 1000000))}.{i.name.split('.')[-1]}"
                        file_one_id_list.append(filename)
                        i.name = filename
                        with open(os.path.join(settings.IMAGES_DIR, filename), 'wb+') as fp:
                            for chunk in i.chunks():
                                fp.write(chunk)
                    update_kw[k] = ','.join(file_one_id_list)
                if k == 'field_img_two':
                    update_kw[k] = update_temp['field_img_two']
                    for i in update_kw[k]:
                        filename = f"{i.name.split('.')[0]}_{int(round(time.time() * 1000000))}.{i.name.split('.')[-1]}"
                        file_two_id_list.append(filename)
                        i.name = filename
                        with open(os.path.join(settings.IMAGES_DIR, filename), 'wb+') as fp:
                            for chunk in i.chunks():
                                fp.write(chunk)
                    update_kw[k] = ','.join(file_two_id_list)
            self.queryset.filter(id=pk).update(**update_kw, updater=request.user.username,
                                                   update_time=timezone.now())
            return Response(response.BUGS_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    def down_bug(self, request, **kwargs):
        """
            下载压缩文件
            :param request:
            :param name: 文件名称
            :return:
        """
        file_name = request.query_params.get('fileName')
        file_path = os.path.join(settings.IMAGES_DIR, file_name)
        if not os.path.isfile(file_path):
            return HttpResponse('Sorry but Not Found the File')
        fp = open(file_path, 'rb+')
        try:
            stream_response = FileResponse(fp)
            stream_response['Content-Type'] = 'application/octet-stream'
            stream_response['Content-Disposition'] = f'attachment;filename="{escape_uri_path(file_name)}"'
        except:
            return HttpResponse("Sorry but Not Found the File")

        return stream_response


