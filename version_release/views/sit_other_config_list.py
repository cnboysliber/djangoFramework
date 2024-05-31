# -*- coding: utf-8 -*-
import json
import pandas as pd
import datetime
from sqlalchemy import create_engine
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


class OtherConfigListView(GenericViewSet):
    """
    版本提测增删改查
    """
    queryset = models.SitOtherConfigData.objects.all()
    serializer_class = serializers.SitOtherConfigDataSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    def get_detail(self, request, **kwargs):
        """
        查询基础提测详情

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        queryset = self.queryset.filter(project_id=pk, status=cnt.ACTIVE)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        更新基础提测信息

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        self.queryset.filter(project_id=pk).update(status=cnt.NOT_ACTIVE)
        json_data = json.loads(request.data.get('jsonData'))
        otherConfigList = json_data['otherConfigList']
        i=0
        for i in range(len(otherConfigList)):
            otherConfigList[i]['project_id']=int(otherConfigList[i]['project_id'])
            if otherConfigList[i]['project']:
                del otherConfigList[i]['project']
                del otherConfigList[i]['id']
        df = pd.DataFrame(otherConfigList)
        result = df
        result.fillna('', inplace=True)
        from FasterRunner.settings.pro import DATABASES
        from django.conf import settings
        host = DATABASES['version_release']['HOST']
        port = 3306
        user = DATABASES['version_release']['USER']
        password = DATABASES['version_release']['PASSWORD']
        database = 'version_release'
        engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(user, password, host, port, database),
            encoding='utf-8')
        con = engine.connect()
        result.to_sql(name='version_release_sitotherconfigdata', con=con, if_exists='append', index=False)
        return Response(response.PERFORM_ADD_CONFIG_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        添加基础提测信息

        :param request:
        :return:
        """

        # 反序列化

        # 反序列化
        json_data = json.loads(request.data.get('jsonData'))
        otherConfigList = json_data['otherConfigList']
        project_id = json_data['project']
        df = pd.DataFrame(otherConfigList)
        result = df
        result['project_id'] = project_id
        result['status'] = 1
        result.fillna('', inplace=True)
        from FasterRunner.settings.pro import DATABASES
        from django.conf import settings
        host = DATABASES['version_release']['HOST']
        port = 3306
        user = DATABASES['version_release']['USER']
        password = DATABASES['version_release']['PASSWORD']
        database = 'version_release'
        engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(user, password, host, port, database),
            encoding='utf-8')
        con = engine.connect()
        result.to_sql(name='version_release_sitotherconfigdata', con=con, if_exists='append', index=False)
        return Response(response.PERFORM_ADD_CONFIG_SUCCESS)
