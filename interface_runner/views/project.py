from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from interface_runner import models, serializers
from FasterRunner import pagination
from rest_framework.response import Response
from interface_runner.utils import response
from interface_runner.utils import prepare
from interface_runner.utils import day
from FasterRunner.utils.decorator import request_log
from interface_runner.utils.runner import DebugCode
from interface_runner.utils.tree import get_tree_max_id


class ProjectView(GenericViewSet):
    """
    项目增删改查
    """
    queryset = models.Project.objects.all().order_by('-update_time')  # 查询集合，重写GenericViewSet的queryset
    serializer_class = serializers.ProjectSerializer  # 实例化，并重写
    pagination_class = pagination.MyCursorPagination  # 实例化，并重写

    @method_decorator(request_log(level='INFO'))
    def list(self, request):
        """
        查询项目信息
        """
        projects = self.get_queryset()  # 获取一个实例化对象
        page_projects = self.paginate_queryset(projects)  # 使用实例化对象
        serializer = self.get_serializer(page_projects, many=True)  # 实例化对象使用序列化器序列化
        res_data = serializer.data  # 获取序列化值
        return self.get_paginated_response(res_data)  # 返回前端，也可以直接使用Response()同样的效果

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """添加项目 {
            name: str
        }
        """

        name = request.data["name"]

        if models.Project.objects.filter(name=name).first():  # 过滤判断是否有重名项目，取第一个数据
            response.PROJECT_EXISTS["name"] = name
            return Response(response.PROJECT_EXISTS)
        # 反序列化
        serializer = serializers.ProjectSerializer(data=request.data)  # 反序列化，解析前端返回来的值为python可读值

        if serializer.is_valid():  # 判断是否为有效的序列化结果
            serializer.save()
            project = models.Project.objects.get(name=name)
            prepare.project_init(project)
            return Response(response.PROJECT_ADD_SUCCESS)

        return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def update(self, request):
        """
        编辑项目
        """

        try:
            project = models.Project.objects.get(id=request.data['id'])  # 获取id对应的project
        except (KeyError, ObjectDoesNotExist):
            return Response(response.SYSTEM_ERROR)

        if request.data['name'] != project.name:  # 获取到的project与传过来的project名称对比，不同则存
            if models.Project.objects.filter(
                    name=request.data['name']).first():  # 如果能在数据库查到对应名称，则提示项目名称已存在，filter返回的是数据，不是对象
                return Response(response.PROJECT_EXISTS)

        # 调用save方法update_time字段才会自动更新
        project.name = request.data['name']
        project.desc = request.data['desc']
        project.responsible = request.data['responsible']
        project.yapi_base_url = request.data['yapi_base_url']
        project.yapi_openapi_token = request.data['yapi_openapi_token']
        project.save()  # 保存数据库

        return Response(response.PROJECT_UPDATE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def delete(self, request):
        """
        删除项目
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            project = models.Project.objects.get(id=request.data['id'])  # get返回的是一个对象

            project.delete()
            prepare.project_end(project)

            return Response(response.PROJECT_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def single(self, request, **kwargs):
        """
        得到单个项目相关统计信息
        """
        pk = kwargs.pop('pk')  # 删除key为pk的键值对对应的值，并返回被删除的value

        try:
            queryset = models.Project.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)

        serializer = self.get_serializer(queryset, many=False)

        project_info = prepare.get_project_detail(pk)
        project_info.update(serializer.data)

        return Response(project_info)


class DebugTalkView(GenericViewSet):
    """
    DebugTalk update，页面上驱动代码那块功能
    """
    # authentication_classes = [OnlyGetAuthenticator, ]
    serializer_class = serializers.DebugTalkSerializer

    @method_decorator(request_log(level='INFO'))
    def list(self, request, **kwargs):
        """
        得到debugtalk code
        """
        project=request.query_params["project"]
        env_id=request.query_params["env_id"]
        try:
            queryset = models.Debugtalk.objects.get(project__id=project,env_id=env_id)
        except ObjectDoesNotExist:
            return Response(response.DEBUGTALK_NOT_EXISTS)

        serializer = self.get_serializer(queryset, many=False)

        return Response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def update(self, request):
        """
        编辑debugtalk.py 代码并保存
        """
        pk = request.data['id']
        try:
            models.Debugtalk.objects.filter(id=pk). \
                update(code=request.data['code'], updater=request.user.username)

        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

        return Response(response.DEBUGTALK_UPDATE_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def run(self, request):
        try:
            code = request.data["code"]
        except KeyError:
            return Response(response.KEY_MISS)
        debug = DebugCode(code)
        debug.run()
        resp = {
            "msg": debug.resp,
            "success": True,
            "code": "0001"
        }
        return Response(resp)


class TreeView(GenericViewSet):
    """
    树形结构操作
    """

    # authentication_classes = [OnlyGetAuthenticator, ]

    @method_decorator(request_log(level='INFO'))
    def get(self, request, **kwargs):
        """
        返回树形结构
        当前最带节点ID
        """
        env_id=None
        tree_type = request.query_params['type']
        try:
            env_id=request.query_params["env_id"]
            tree = models.Relation.objects.filter(project__id=kwargs['pk'], type=tree_type,env_id=env_id).first()
        # except KeyError:
        #     return Response(response.KEY_MISS)
        #
        # except ObjectDoesNotExist:
        #     return Response(response.SYSTEM_ERROR)
        except:
            tree = models.Relation.objects.filter(project__id=kwargs['pk'], type=tree_type).first()

        if tree:
            body = eval(tree.tree)  # list
            tree = {
                "tree": body,
                "id": tree.id,
                "env_id" : env_id,
                "success": True,
                "max": get_tree_max_id(body)
            }
            return Response(tree)
        else:
            return Response(response.TREE_NO_DATA)


    def add(self,request,**kwargs):
        """
        新增树形结构
        """
        try:
            body = request.data.pop('body')
            env_id=request.data['env_id']
            type=request.data['type']
            project=request.data['project']

            project_obj=models.Project.objects.get(id=project)

            if not models.Project.objects.filter(id=project).first():
                return Response(response.PROJECT_NOT_EXISTS)

            request.data['tree']=body
            request.data['project']=project_obj
            models.Relation.objects.create(**request.data)

        except KeyError:
            return Response(response.KEY_MISS)

        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

        return Response(response.TREE_ADD_SUCCESS)


    @method_decorator(request_log(level='INFO'))
    def patch(self, request, **kwargs):
        """
        修改树形结构，ID不能重复
        """
        try:
            body = request.data['body']
            mode = request.data['mode']

            relation = models.Relation.objects.get(id=kwargs['pk'])
            relation.tree = body
            relation.save()

        except KeyError:
            return Response(response.KEY_MISS)

        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

        #  mode -> True remove node
        if mode:
            prepare.tree_end(request.data, relation.project)

        response.TREE_UPDATE_SUCCESS['tree'] = body
        response.TREE_UPDATE_SUCCESS['max'] = get_tree_max_id(body)

        return Response(response.TREE_UPDATE_SUCCESS)


class VisitView(GenericViewSet):
    serializer_class = serializers.VisitSerializer
    queryset = models.Visit.objects

    def list(self, request):
        project = request.query_params.get("project")
        # 查询当前项目7天内的访问记录
        # 根据日期分组
        # 统计每天的条数
        count_data = self.get_queryset() \
            .filter(project=project, create_time__range=(day.get_day(-6), day.get_day(1))) \
            .extra(select={"create_time": "DATE_FORMAT(create_time,'%%m-%%d')"}) \
            .values('create_time') \
            .annotate(counts=Count('id')).values('create_time', 'counts')

        create_time = []
        count = []
        for d in count_data:
            create_time.append(d['create_time'])
            count.append(d['counts'])
        return Response({'create_time': create_time, 'count': count})
#
# class FileView(APIView):
#
#     def post(self, request):
#         """
#         接收文件并保存
#         """
#         file = request.FILES['file']
#
#         if models.FileBinary.objects.filter(name=file.name).first():
#             return Response(response.FILE_EXISTS)
#
#         body = {
#             "name": file.name,
#             "body": file.file.read(),
#             "size": get_file_size(file.size)
#         }
#
#         models.FileBinary.objects.create(**body)
#
#         return Response(response.FILE_UPLOAD_SUCCESS)
