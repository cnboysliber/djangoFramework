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
from FasterRunner import const as cnt


class GitProjectsView(GenericViewSet):
    """
    获取产品线
    """
    queryset = models.GitProgrammeData.objects.all()
    serializer_class = serializers.GitProgrameSerializer
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
        pk = request.query_params.get("project_name")
        queryset = self.queryset.filter(project_name=pk).first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def get_sevice_detail(self, request, **kwargs):
        """
        新建服务根据项目名称获取项目信息

        :param request:
        :return:
        """
        pk = json.loads(request.query_params.get("params"))
        pk = pk['assembly_name']
        queryset = self.queryset.filter(programme_name=pk).first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def get_branches(self,request,**kwargs):
        '''
        获取对应项目branches
        '''
        branches = []
        for j in range(1,12):
            pk = kwargs.get('pk')
            Url = 'https://git.fcb.com.cn/api/v4/projects/' + pk + '/repository/branches?page=' + str(j)

            if pk:
                headers={
                    'PRIVATE-TOKEN':"d7wY6MKQDtPXQ6Wsbar8"
                }
                response = requests.get(url=Url, headers=headers).json()
                if len(response) == 0:
                    break
                else:
                    i = 0
                    for i in range(len(response)):
                        branch=response[i]['name']
                        branches.append(branch)
                        i += 1
                        continue
            # continue
        return HttpResponse(json.dumps(branches))

    def get_tag(self,request,**kwargs):
        '''
        获取对应组件tag
        '''
        tags = []
        for j in range(1, 3):
            pk = kwargs.get('pk')
            Url = 'https://git.fcb.com.cn/api/v4/projects/' + pk + '/repository/tags?page=' + str(j)
            if pk:
                headers={
                    'PRIVATE-TOKEN':"d7wY6MKQDtPXQ6Wsbar8"
                }
                response = requests.get(url=Url, headers=headers).json()

                if len(response) == 0:
                    break
                else:
                    i = 0
                    for i in range(len(response)):
                        tag=response[i]['name']
                        tags.append(tag)
                        i += 1
                        continue
            else:
                break

        return HttpResponse(json.dumps(tags))

    def get_commitID(self,request,**kwargs):
        '''
        获取对应组件tag
        '''
        pk = kwargs.get('pk')
        # branch_name = request.query_params.get("branch_name")  #
        # Url = 'https://git.fcb.com.cn/api/v4/projects/' + str(pk) + '/repository/commits?ref_name='+str(branch_name)
        Url = 'https://git.fcb.com.cn/api/v4/projects/' + str(pk) + '/repository/commits'
        # Url='https://git.fcb.com.cn/api/v4/projects/112/repository/commits?ref_name=master'
        if pk:
            headers={
                'PRIVATE-TOKEN':"d7wY6MKQDtPXQ6Wsbar8"
            }
            response = requests.get(url=Url, headers=headers).json()
            commits_id = []
            i = 0
            for i in range(len(response)):
                id=response[i]['id']
                commits_id.append(id)
                i += 1
                continue
            return HttpResponse(json.dumps(commits_id))
        else:
            return HttpResponse('')

    def get_project_name(self,request,**kwargs):
        '''
        获取所有的组件名
        '''
        pk = request.query_params.get("assembly_name")
        # pk = request.query_params.get("assembly_name")#得到前端传的工程名称
        project_name = models.GitProgrammeData.objects.values('project_name').distinct()
        project_name=project_name.filter(programme_name=pk)
        return Response(project_name)


    def get_project_list(self,request,**kwargs):
        '''
        获取所有的组件名
        '''
        # connect=pymysql.connect(host='127.0.0.1',user='root',password='root',db = 'version',charset = 'utf8')
        # cursor=connect.cursor()
        # SQL='select project_name from version_release_gitprogrammedata'
        # cursor.execute(SQL)
        # results = cursor.fetchall()
        # cursor.close()
        # connect.close()
        results = models.GitProgrammeData.objects.values('project_name').distinct()
        i=0
        data = []
        for i in range(len(results)):
            value=str(results[i]).lstrip("('").rstrip("',)")
            data.append(value)
        return Response(data)

    def get_programe_list(self, request, **kwargs):
        '''
        获取所有的工程名称
        '''
        programme_name = models.GitProgrammeData.objects.values('programme_name').distinct()
        print(programme_name)
        return Response(programme_name)




