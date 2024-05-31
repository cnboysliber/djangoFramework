import datetime, requests
import json,os,openpyxl,xlwt
import pandas as pd
from io import BytesIO
import traceback
from django.utils.encoding import escape_uri_path
from django.http import StreamingHttpResponse,HttpResponse
from loguru import logger
from openpyxl import Workbook
from xlrd import xldate_as_tuple
from django.db.models import Count
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from FasterRunner import pagination
from FasterRunner import const as cnt
from quality_management import models
from quality_management import serializers
from quality_management.utils import response
from FasterRunner.utils.decorator import request_log


# def filetostream(filename, streamlength=512):
#     file = open(filename, 'rb')
#     while True:
#         stream = file.read(streamlength)
#         if stream:
#             yield stream
#         else:
#             break

class GitCommitApiView(GenericViewSet):
    """
    git 提交commit数据
    """
    queryset = models.GitCommitData.objects.all()
    serializer_class = serializers.GitCommitDataSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    @method_decorator(request_log(level='INFO'))
    def add_commit(self, request):
        """
        commit数据

        :param request:
        :return:
        """
        # 反序列化
        model_data = get_gitProject_branch_commit_list()
        model_data = [models.GitCommitData(**data) for data in model_data]
        print(model_data)
        if model_data:
            models.GitCommitData.objects.bulk_create(model_data)
        resp = response.PERFORM_UPLOAD_SUCCESS
        return Response(resp)

    @method_decorator(request_log(level='INFO'))
    def list_file(self, request):
        """
        数据导出

        :param request:
        :return:
        """
        filename = 'total.xls'
        # if os.path.exists(filename):
        #     os.remove(filename)
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = "attachment; filename={}".format(filename)
        workbook = xlwt.Workbook('utf-8')
        workname=workbook.add_sheet('sheet')
        projects = models.GitCommitData.objects.all()
        serializer = self.get_serializer(projects, many=True)
        contents=json.loads(json.dumps(serializer.data,ensure_ascii=False))
        contents_list=['id','git_project_id','project_name','branch','commit_id','title','message','git_type','author_name','committed_date','additions','deletions','total']
        for i in range(len(contents_list)):
            workname.write(0,i,contents_list[i])
        excel_row = 1
        for content_index,content_data in enumerate(contents):
            workname.write(excel_row, 0, content_data['git_project_id'])
            workname.write(excel_row, 1, content_data['project_name'])
            workname.write(excel_row, 2, content_data['branch'])
            workname.write(excel_row, 3, content_data['commit_id'])
            workname.write(excel_row, 4,  content_data['title'])
            workname.write(excel_row, 5,  content_data['message'])
            workname.write(excel_row, 6,  content_data['git_type'])
            workname.write(excel_row, 7, content_data['author_name'])
            workname.write(excel_row, 8,  content_data['committed_date'])
            workname.write(excel_row, 9, content_data['additions'])
            workname.write(excel_row, 10,  content_data['deletions'])
            workname.write(excel_row, 11,  content_data['total'])
            excel_row += 1
        workbook.save(response)
        return response

    @method_decorator(request_log(level='DEBUG'))
    def web_top_list(self, request):
        """
        代码量数据

        :param request:
        :return:
        """
        month = request.query_params.get("month", '')
        page_num = request.query_params.get("page_num", '')
        num=int(page_num[:2])
        if month != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(total__lt=1000).filter(total__gt=0)
            projects_fileter = projects_fileters.filter(committed_date__contains=month)
            projects_fileter = projects_fileter.distinct().order_by('-total')[:num]
        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(total__lt=1000).filter(total__gt=0)
            projects_fileter = projects_fileter.distinct().order_by('-total')[:num]
        print(projects_fileter)
        print('---------------------------')
        serializer = self.get_serializer(projects_fileter, many=True,read_only=True)
        print(serializer.data)
        print('++++++++++++++++++++++++++')
        return Response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def web_bottom_list(self, request):
        """
        代码量数据

        :param request:
        :return:
        """
        month = request.query_params.get("month", '')
        page_num = request.query_params.get("page_num", '')
        num=int(page_num[:2])
        if month != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(total__lt=1000).filter(total__gt=0)
            projects_fileter = projects_fileters.filter(committed_date__contains=month)
            projects_fileter = projects_fileter.order_by('total')[:num]
        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(total__lt=1000).filter(total__gt=0)
            projects_fileter = projects_fileter.order_by('total')[:num]
        serializer = self.get_serializer(projects_fileter, many=True)
        return Response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def web_no_data_list(self, request):
        """
        代码量数据

        :param request:
        :return:
        """
        month = request.query_params.get("month", '')
        page_num = request.query_params.get("page_num", '')
        num=int(page_num[:2])
        if month != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(total=0)
            projects_fileter = projects_fileters.filter(committed_date__contains=month)
            projects_fileter = projects_fileter.order_by('total')[:num]
        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(total=0)
            projects_fileter = projects_fileter.order_by('total')[:num]
        serializer = self.get_serializer(projects_fileter, many=True)
        return Response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def api_top_list(self, request):
        """
        代码量数据

        :param request:
        :return:
        """
        month = request.query_params.get("month", '')
        page_num = request.query_params.get("page_num", '')
        num=int(page_num[:2])
        if month != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(total__lt=1000).filter(total__gt=0)
            projects_fileter = projects_fileters.filter(committed_date__contains=month)
            projects_fileter = projects_fileter.order_by('-total')[:num]
        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(total__lt=1000).filter(total__gt=0)
            projects_fileter = projects_fileter.order_by('-total')[:num]
        serializer = self.get_serializer(projects_fileter, many=True)
        return Response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def api_bottom_list(self, request):
        """
        代码量数据

        :param request:
        :return:
        """
        month = request.query_params.get("month", '')
        page_num = request.query_params.get("page_num", '')
        num=int(page_num[:2])
        if month != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(total__lt=1000).filter(total__gt=0)
            projects_fileter = projects_fileters.filter(committed_date__contains=month)
            projects_fileter = projects_fileter.order_by('total')[:num]
        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(total__lt=1000).filter(total__gt=0)
            projects_fileter = projects_fileter.order_by('total')[:num]
        serializer = self.get_serializer(projects_fileter, many=True)
        return Response(serializer.data)

    @method_decorator(request_log(level='DEBUG'))
    def api_no_data_list(self, request):
        """
        代码量数据

        :param request:
        :return:
        """
        month = request.query_params.get("month", '')
        page_num = request.query_params.get("page_num", '')
        num=int(page_num[:2])
        if month != '':
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileters = projects.filter(total=0)
            projects_fileter = projects_fileters.filter(committed_date__contains=month)
            projects_fileter = projects_fileter.order_by('total')[:num]
        else:
            projects = self.get_queryset()  # 获取一个实例化对象
            projects_fileter = projects.filter(total=0)
            projects_fileter = projects_fileter.order_by('total')[:num]
        serializer = self.get_serializer(projects_fileter, many=True)
        return Response(serializer.data)


get_git_all_url = 'http://git.fcb.com.cn/api/v4/projects/'
get_project_branch_url = get_git_all_url + '{}/repository/branches'
get_branch_commit_url = get_git_all_url + '{}/repository/commits'
get_commit_msg_url = get_git_all_url + '{}/repository/commits/{}'
base_token = 'd7wY6MKQDtPXQ6Wsbar8'


def get_git_project_id():
    """
    :param private_token: gitlab个人token，请在gitlab上生产
    :param project_repo_url: http://xxxx.git，需要带上.git
    :return:
    """
    project_list = []

    params_dict = {'private_token': base_token, 'per_page': 100}
    for i in range(1, 101):
        params_dict['page'] = i
        response = requests.get(url=get_git_all_url, params=params_dict)
        print(response.text)
        if len(json.loads(response.text)) > 0:
            msg_dict = json.loads(response.text)
            for j in range(len(msg_dict)):
                if 'id' in msg_dict[j].keys():
                    if not msg_dict[j]['id']:
                        break
                    item_list = {}
                    item_list['id'] = msg_dict[j]['id']
                    item_list['name'] = msg_dict[j]['name']
                    project_list.append(item_list)
        else:
            break
    return project_list


def get_git_project_branchs(git_project_id):
    """

    :param private_token: gitlab个人token，请在gitlab上生产
    :param git_project_id: 字符串类型，项目id
    :return:
    """

    branch_list = []
    if all([base_token, git_project_id]):
        param_dict = {'private_token': base_token, 'per_page': 100}
        for i in range(1, 101):
            param_dict['page'] = i
            response = requests.get(url=get_project_branch_url.format(git_project_id), params=param_dict)
            print(response.text)
            if len(response.text) <= 2:
                break
            elif response.status_code == 200:
                msg_dict = json.loads(response.text)
                for j in range(len(msg_dict)):
                    if 'name' in msg_dict[j].keys():
                        if not msg_dict[j]['name']:
                            break
                        branch_list.append(msg_dict[j]['name'])
    return branch_list


def get_branch_commit(git_project_id, branch_name, begin_time=None):
    """

    :param private_token: gitlab的token
    :param git_project_id: git项目id
    :param branch_name: 分支名称
    :param begin_time: 从这开始之后的commit时间
    :return:
    """
    commit_list = []
    if all([git_project_id, branch_name]):
        para_dict = {'private_token': base_token, 'ref_name': branch_name}

        if not begin_time:
            para_dict['per_page'] = 10
            response = requests.get(url=get_branch_commit_url.format(git_project_id), params=para_dict)
            print(response.text)
            if response.status_code == 200:
                msg_dict = json.loads(response.text)
                for i in range(len(msg_dict)):
                    if 'id' in msg_dict[i].keys():
                        commit_id = msg_dict[i]['id']
                        commit_list.append(commit_id)
        else:
            para_dict['per_page'] = 100
            for i in range(1, 101):
                para_dict['page'] = i
                response = requests.get(url=get_branch_commit_url.format(git_project_id), params=para_dict)
                print(response.text)
                if response.status_code == 200:
                    msg_dict = json.loads(response.text)
                    for j in range(len(msg_dict)):
                        # 这里有三个时间，不确定是哪个，先全部拿下来，暂时用committed_data_time
                        id = msg_dict[j]['id']
                        authored_data_time = msg_dict[j]['authored_date']
                        committed_data_time = msg_dict[j]['committed_date']
                        created_at_time = msg_dict[j]['created_at']
                        if compare_time(committed_data_time, begin_time):
                            commit_list.append(id)
    return commit_list


def get_commit_msg(branch, git_oroject_name, git_project_id, commit_id):
    commit_msg_dict = {}
    if all([base_token, git_project_id, commit_id]):
        para_dict = {'private_token': base_token}
        response = requests.get(url=get_commit_msg_url.format(git_project_id, commit_id), params=para_dict)
        print(response.text)
        if response.status_code == 200:
            msg_dict = json.loads(response.text)
            commit_msg_dict['git_project_id'] = git_project_id
            commit_msg_dict['project_name'] = git_oroject_name
            commit_msg_dict['branch'] = branch
            commit_msg_dict['commit_id'] = msg_dict['id']
            commit_msg_dict['title'] = msg_dict['title']
            if 'feat' in msg_dict['title'].lower():
                commit_msg_dict['git_type'] = 'feat'
            elif 'fix' in msg_dict['title'].lower():
                commit_msg_dict['git_type'] = 'fix'
            elif 'merge' in msg_dict['title'].lower():
                commit_msg_dict['git_type'] = 'merge'
            else:
                commit_msg_dict['git_type'] = 'update'
            commit_msg_dict['author_name'] = msg_dict['author_name']
            commit_msg_dict['committed_date'] = msg_dict['committed_date']
            commit_msg_dict['additions'] = msg_dict['stats']['additions']
            commit_msg_dict['deletions'] = msg_dict['stats']['deletions']
            commit_msg_dict['additions'] = msg_dict['stats']['additions']
            commit_msg_dict['deletions'] = msg_dict['stats']['deletions']
            commit_msg_dict['total'] = msg_dict['stats']['total']
    return commit_msg_dict


def get_gitProject_branch_commit_list():  # , project_repo_url, branch, begin_time=None
    """
    f返回commit提交数据信息
    :param :private_token:
    :return:
    """
    commit_list = []
    try:
        # git_project_id = get_git_project_id()
        git_project_id = [{"id": 1079, "name": "bigdata_tools"}, {"id": 1076, "name": "fcb-tradecenter-h5"},
                          {"id": 1075, "name": "saasweb"}, {"id": 1074, "name": "fcb-base-components-mp"},
                          {"id": 1073, "name": "hdb-sql-newscript"}, {"id": 1072, "name": "k8s-intro"},
                          {"id": 1071, "name": "fcb-activity-script"}, {"id": 1070, "name": "PureLayout"},
                          {"id": 1069, "name": "e2ioi"}]
        if git_project_id:
            for item in git_project_id:
                git_project_branch = get_git_project_branchs(git_project_id=item['id'])
                if git_project_branch:
                    for git_project_branch_name in git_project_branch:
                        branch_commit_list = get_branch_commit(
                            git_project_id=item['id'],
                            branch_name=git_project_branch_name,
                        )
                        if branch_commit_list:
                            for i in range(len(branch_commit_list)):
                                commit_msg_dict = get_commit_msg(branch=git_project_branch_name,
                                                                 git_oroject_name=item['name'],
                                                                 git_project_id=item['id'],
                                                                 commit_id=branch_commit_list[i])

                                if commit_msg_dict:
                                    commit_list.append(commit_msg_dict)
    except Exception as e:
        print('异常信息为：{}'.format(e))
    return commit_list


def compare_time(time1, time2_compare):
    if any(key in time1 for key in ['T', '+08:']):
        time1 = time1.replace('T', ' ').replace('+08:', '')
    d1 = datetime.datetime.strptime(time1, '%Y-%m-%d %H:%M:%S.%f')
    d2 = datetime.datetime.strptime(time2_compare, '%Y-%m-%d %H:%M:%S.%f')
    delta = d1 - d2
    print(delta.total_seconds())
    if delta.total_seconds() >= 0:
        return True
    else:
        return False
