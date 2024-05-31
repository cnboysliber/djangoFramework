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



class AccountConfigView(GenericViewSet):
    serializer_class = serializers.AccountConfigSeSerializer  #初始化的时候，就已经给前端返回的request进行了序列化，所以下方每个函数接收到的request都可以直接拿数据
    queryset = models.AccountConfig.objects


    def list(self,request):
        '''
        查询
        {
            "project":1,
            "search":""
        }
        '''
        project=request.query_params["project"]
        search=request.query_params["search"]
        env_id=request.query_params["env_id"]

        queryset=self.get_queryset().filter(project_id=project,env_id=env_id).order_by("update_time")

        if search!="":  #查询条件
            queryset=self.queryset.filter(project_id=project,env_id=env_id).filter(Q(ac_name__contains=search))

        page_queryset=self.paginate_queryset(queryset)
        serializer=self.serializer_class(page_queryset,many=True)  #many=True指包含多个对象，查询出的结果才能包含多个对象，默认返回10条结果
        return  self.get_paginated_response(serializer.data)


    @method_decorator(request_log(level='INFO'))
    def add(self,request):
        '''
        新增
        {
            "ac_name": "hdb_prod",
            "ac_info": {},
            "description":"案场宝登录账号",
            "project": "1"
        }
        '''

        ac_info=request.data.get("ac_info")
        ac_name=request.data.get("ac_name")
        description=request.data.get("description")
        project=request.data.get("project")
        # env_id=request.data.get('env_id')
        ser=self.serializer_class(data=request.data)

        if ser.is_valid():
            check_res=self.serializer_class().ac_info_check(eval(ac_info))  #校验db_info字段格式
            if  check_res:
                response.ACCOUNT_FAIL['msg']=check_res
                return Response(response.ACCOUNT_FAIL)

            project_obj=models.Project.objects.filter(id=project).first()
            if not project_obj:   #判断项目是否存在
                return Response(response.PROJECT_NOT_EXISTS)

            if  models.AccountConfig.objects.filter(ac_name=ac_name,project_id=project):
                return Response(response.ACCOUNT_EXISTS)

            request.data["project"]=project_obj  #外键需要传入一个查询对象，才能写入数据库
            request.data['creator']=request.user.username
            models.AccountConfig.objects.create(**request.data)
            return Response(response.ACCOUNT_ADD_SUCCESS)

        else:

            response.ACCOUNT_FAIL['msg']=ErrorProcessor().error_pro(ser.errors)  #字段校验错误直接返回给设定好的response
            return Response(response.ACCOUNT_FAIL)



    @method_decorator(request_log(level="INFO"))
    def update(self,request,**kwargs):
        '''
        单个更新
        {
        "ac_name": "hdb_prod",
        "ac_info": {},
        "description":"产品中心数据库",
        "project": "1",
        "id":12
        }
        '''
        project_id=kwargs['pk']
        ac_id=request.data["id"]
        ac_name=request.data["ac_name"]
        ac_info=request.data["ac_info"]
        description=request.data["description"]
        fixture_name=request.data["fixture_name"]
        env_id=request.data['env_id']

        ac_config=models.AccountConfig.objects.filter(id=ac_id).first()
        if fixture_name:
            fixture_id=models.Fixture.objects.get(name=fixture_name,env_id=env_id,project_id=project_id).id
        if not ac_config:#校验是否存在数据
            return Response(response.ACCOUNT_NOT_EXISTS)

        if models.AccountConfig.objects.exclude(id=ac_id).filter(project_id=project_id,ac_name=ac_name).first():
            return Response(response.ACCOUNT_EXISTS)

        ac_obj=models.AccountConfig.objects.get(id=ac_id)
        ac_obj.ac_name=ac_name
        ac_obj.ac_info=ac_info
        ac_obj.description=description
        ac_obj.fixture_id=fixture_id
        ac_obj.updater=request.user.username
        ac_obj.save()

        return Response(response.ACCOUNT_UPDATE_SUCCESS)




    def delete(self,request,**kwargs):
        '''
        删除一个变量使用 pk
        删除多个使用body
        [{
            id:1,
            project_id:1,
            ...
        },
        {
            id:1,
            project_id:1,
            ...
        }
        ]
        '''
        try:
            if kwargs.get('pk'):  # 单个删除
                models.AccountConfig.objects.get(id=kwargs['pk']).delete()
            else:
                for content in request.data:
                    models.AccountConfig.objects.get(id=content['id']).delete()

        except ObjectDoesNotExist:
            return Response(response.ACCOUNT_NOT_EXISTS)

        return Response(response.ACCOUNT_DEL_SUCCESS)
