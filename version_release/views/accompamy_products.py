# -*- coding: utf-8 -*-
import os,json
import pandas as pd
import xlrd
import shutil
from xlrd import xldate_as_tuple
from datetime import datetime
from loguru import logger
from sqlalchemy import create_engine
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


class AccompanyProductsView(GenericViewSet):
    """
    获取获取业务线
    """
    queryset = models.AccompanyTestList.objects.all()
    serializer_class = serializers.AccompanyProductsSerializer
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
        serializer = self.get_serializer(projects, many=True)
        res_data=serializer.data
        accompany_list=[]
        list=json.loads(json.dumps(res_data))
        for i in range(len(list)):
            accompany_list.append({"value": list[i]['accompany_products'].strip(), "label": list[i]['accompany_products'].strip()})
        return Response(accompany_list)
