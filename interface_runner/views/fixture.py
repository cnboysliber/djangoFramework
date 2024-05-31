from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework.viewsets import GenericViewSet
from interface_runner import models, serializers
from rest_framework.response import Response
from interface_runner.utils import response
from FasterRunner.utils.decorator import request_log
from interface_runner.utils.parser import ErrorProcessor


class FixtureViewSet(GenericViewSet):
    serializer_class = serializers.FixtureSerializer
    queryset = models.Fixture.objects


    def list(self,request):
        project_id = request.query_params["project"]
        env_id=request.query_params["env_id"]
        # search = request.query_params["search"]

        queryset = self.get_queryset().filter(project_id=project_id,env_id=env_id).order_by("update_time")


        if "id" in request.query_params.keys():     #传来id时，证明只需要一条数据

            fixture_id=request.query_params["id"]
            queryset=self.get_queryset().filter(project_id=project_id,id=fixture_id,env_id=env_id)

        # if search != "":  # 查询条件
        #     queryset = self.queryset.filter(project_id=project).filter(Q(db_name__contains=search))

        page_queryset = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page_queryset, many=True)  # many=True指包含多个对象，查询出的结果才能包含多个对象，默认返回10条结果
        return self.get_paginated_response(serializer.data)


    def add(self,request):
        '''
        {
            "project_id":"",
            "name":"",
            "desc":"",
            "code":"",
            "creator":"",
        }
        '''
        name=request.data.get("name")
        project_id=request.data.get("project")

        ser=self.serializer_class(data=request.data)

        if ser.is_valid():
            if not models.Project.objects.filter(id=project_id):
                return  Response(response.PROJECT_NOT_EXISTS)

            if models.Fixture.objects.filter(project_id=project_id,name=name):
                return Response(response.FIXTURE_EXISTS)

            project_obj = models.Project.objects.filter(id=project_id).first()  #外键需要传入对象
            request.data["project"]=project_obj
            request.data['creator']=request.user.username
            models.Fixture.objects.create(**request.data)

            return Response(response.FIXTURE_ADD_SUCCESS)

        else:

            response.FIXTURE_FAIL['msg']=ErrorProcessor().error_pro(ser.errors)  #字段校验错误直接返回给设定好的response
            return Response(response.FIXTURE_FAIL)


    def update(self,request):
        '''
                {
                    "project":"",
                    "name":"",
                    "desc":"",
                    "code":"",
                    "updater":"",
                    "id":""
                }
                '''

        name = request.data.get("name")
        project_id = request.data.get("project")
        id=request.data.get("id")

        ser = self.serializer_class(data=request.data)


        if ser.is_valid():
            if not models.Project.objects.filter(id=project_id).first():
                return Response(response.PROJECT_NOT_EXISTS)

            if models.Fixture.objects.exclude(id=id).filter(project_id=project_id,name=name).first():
                return Response(response.FIXTURE_EXISTS)


            update_obj = models.Fixture.objects.get(id=id)

            update_obj.name=name
            update_obj.desc=request.data.get("desc")
            update_obj.code=request.data.get("code")
            update_obj.updater=request.user.username

            update_obj.save()

            return Response(response.FIXTURE_UPDATE_SUCCESS)

    def delete(self,request,**kwargs):
        '''
            {
                "project":"",
                "id":""
            }
        '''
        try:
            if kwargs.get('pk'):  # 单个删除
                models.Fixture.objects.get(id=kwargs['pk']).delete()
            else:
                for content in request.data:
                    models.Fixture.objects.get(id=content['id']).delete()

        except ObjectDoesNotExist:
            return Response(response.FIXTURE_NOT_EXISTS)

        return Response(response.FIXTURE_DEL_SUCCESS)
        