from copy import deepcopy

from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework.viewsets import GenericViewSet
from interface_runner import models, serializers
from rest_framework.response import Response
from interface_runner.utils import response
from FasterRunner.utils.decorator import request_log
from interface_runner.utils.parser import ErrorProcessor



class EnvView(GenericViewSet):
    serializer_class = serializers.EnvSerializer  #初始化的时候，就已经给前端返回的request进行了序列化，所以下方每个函数接收到的request都可以直接拿数据
    queryset = models.Env.objects


    def list(self,request):
        '''
        查询
        {
            "project":1,
            "search":""
        }
        '''
        # env_id=request.query_params["env_id"]
        # search=request.query_params["search"]

        queryset=self.get_queryset().filter().order_by("update_time")

        # if search!="":  #查询条件
        #     queryset=self.queryset.filter(project_id=project).filter(Q(db_name__contains=search))

        page_queryset=self.paginate_queryset(queryset)
        serializer=self.serializer_class(page_queryset,many=True)  #many=True指包含多个对象，查询出的结果才能包含多个对象，默认返回10条结果
        return  self.get_paginated_response(serializer.data)