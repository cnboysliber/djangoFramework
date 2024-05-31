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


class ProductView(GenericViewSet):
    """
    获取产品线
    """
    queryset = models.ProductLineManage.objects.all()
    serializer_class = serializers.ProductSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        查询服务列表

        :param request:
        :return:
        """
        projects = self.get_queryset()  # 获取一个实例化对象
        pagination_queryset = self.paginate_queryset(projects)
        serializer = self.get_serializer(pagination_queryset, many=True)
        # res_data=serializer.data
        # print(res_data)
        return self.get_paginated_response(serializer.data)





