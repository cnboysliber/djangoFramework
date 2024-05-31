# -*- coding: utf-8 -*-
import requests
from django.utils.decorators import method_decorator
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from FasterRunner import pagination
from version_release import models
from version_release import serializers
from version_release.utils import response
from FasterRunner.utils.decorator import request_log
from django.http import HttpResponse
import json,pymysql
import pandas as pd
import datetime

try:
    from sqlalchemy import create_engine
    from FasterRunner import const as cnt
except Exception as e:
    print(e)


class RaiseOtherView(GenericViewSet):
    """
    获取产品线
    """
    queryset = models.RaiseOtherData.objects.all()
    serializer_class = serializers.RaiseOtherDataSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        获取git项目数据

        :param request:
        :return:
        """
        projects = self.get_queryset()  # 获取一个实例化对象
        pagination_queryset = self.paginate_queryset(projects)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        根据项目名称获取项目信息

        :param request:
        :return:
        """
        business_line = request.query_params.get("business_line")
        product_line = request.query_params.get("product_line")
        assembly_name = request.query_params.get("assembly_name")
        apply_time = request.query_params.get("apply_time")
        print(business_line,product_line,assembly_name,apply_time)
        queryset = self.queryset.filter(business_line=str(business_line)).filter(product_line=str(product_line)).filter(assembly_name=str(assembly_name)).filter(apply_time=str(apply_time)).first()
        print(queryset)
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
        json_data = json.loads(request.data.get('jsonData'))
        print(json_data)
        sql_data=json_data['sqltablelist']
        data_data = json_data['datatablelist']
        other_data = json_data['othertablelist']
        business_line=json_data['business_line']
        product_line = json_data['product_line']
        assembly_name = json_data['assembly_name']
        apply_time = json_data['apply_time']
        df=pd.DataFrame(sql_data)
        df_long=len(df)
        df_data=pd.DataFrame(data_data)
        df_data_long = len(df)
        df_other = pd.DataFrame(other_data)
        df_other_long = len(df)
        max_long=max(df_long,df_other_long,df_data_long)
        if df_long==max_long:
            result=df.join(df_data).join(df_other)
        elif df_data_long== max_long:
            result = df_data.join(df).join(df_other)
        else:
            result = df_other.join(df_data).join(df)

        result['business_line']=business_line
        result['product_line']=product_line
        result['assembly_name'] = assembly_name
        result['apply_time'] = datetime.date.today()
        result.fillna('',inplace=True)
        from FasterRunner.settings.pro import DATABASES
        # host = '127.0.0.1'
        host=DATABASES['version_release']['HOST']
        port = 3306
        user = DATABASES['version_release']['USER']
        password = DATABASES['version_release']['PASSWORD']
        database = 'version_release'
        engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(user, password, host, port, database),
            encoding='utf-8')
        con = engine.connect()
        result.to_sql(name='version_release_raiseotherdata',con=con,if_exists='append',index=False)

        return Response('')

