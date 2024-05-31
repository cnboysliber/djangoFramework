import json
import time

from crontab import CronTab
from django.db.models import Q
from rest_framework import serializers

from interface_runner import models
from interface_runner.utils.parser import Parse
from interface_runner.utils import response
from rest_framework import status
from rest_framework.response import Response
from FasterRunner.utils.celeryModel import celery_models

from interface_runner.utils.tree import get_tree_relation_name


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目信息序列化
    """

    api_cover_rate = serializers.SerializerMethodField()

    class Meta:  #定义了需要序列化、反序列化的字段，与下方AssertSerializer里面的按字段序列化效果基本一致，两者继承不一样，使用ModelSerializer的更节省时间
        model = models.Project
        fields = ['id', 'name', 'desc', 'responsible', 'update_time', 'creator', 'updater', 'yapi_openapi_token', 'yapi_base_url', 'api_cover_rate']

    def get_api_cover_rate(self, obj):
        """
        接口覆盖率，百分比后去两位小数点
        """
        apis = models.API.objects.filter(project_id=obj.id, delete=0).values('interface_path', 'method')
        api_unique = {f'{api["interface_path"]}_{api["method"]}' for api in apis}
        case_suit_info = models.CaseSuitInfo.objects.filter(case__project_id=obj.id).filter(~Q(method='config')).values('interface_path', 'method')
        case_suit_unique = {f'{case_suit["interface_path"]}_{case_suit["method"]}' for case_suit in case_suit_info}
        if len(api_unique) == 0:
            return '0.00'
        if len(case_suit_unique) > len(api_unique):
            return '100.00'
        return '%.2f' % (len(case_suit_unique & api_unique) / len(api_unique) * 100)


class VisitSerializer(serializers.ModelSerializer):
    """
    访问统计序列化
    """

    class Meta:
        model = models.Visit
        fields = '__all__'


class DebugTalkSerializer(serializers.ModelSerializer):
    """
    驱动代码序列化
    """

    class Meta:
        model = models.Debugtalk
        # fields = ['id', 'code', 'creator', 'updater']
        fields = '__all__'


class RelationSerializer(serializers.ModelSerializer):
    """
    树形结构序列化
    """

    class Meta:
        model = models.Relation
        fields = '__all__'


class AssertSerializer(serializers.Serializer):
    class Meta:
        models = models.API

    # 具有验证需要序列化数据的功能，一旦序列化数据不符合这部分验证规则，就会序列化失败。验证标志包括：required、max_length和default。
    node = serializers.IntegerField(min_value=0, default='')
    # max_value=models.Project.objects.latest('id').id 会导致数据库迁移找不到project
    project = serializers.IntegerField(required=True, min_value=1)
    search = serializers.CharField(default='')
    tag = serializers.ChoiceField(choices=models.API.TAG, default='')
    rigEnv = serializers.ChoiceField(choices=models.API.ENV_TYPE, default='')
    delete = serializers.ChoiceField(choices=(0, 1), default=0)
    onlyMe = serializers.BooleanField(default=False)
    showYAPI = serializers.BooleanField(default=True)


# 用例反序列化验证器
class CaseSearchSerializer(serializers.Serializer):
    node = serializers.IntegerField(min_value=0, default='')   #指定解析后的数据类型，比如解析后是字符串，或int,或者日期类型的校验等
    project = serializers.IntegerField(required=True, min_value=1)
    search = serializers.CharField(default='')
    searchType = serializers.CharField(default='')
    caseType = serializers.CharField(default='')
    onlyMe = serializers.BooleanField(default=False)
    env_id =serializers.IntegerField(required=True)


class CaseSuitSerializer(serializers.ModelSerializer):
    """
    用例信息序列化
    """
    case_tag = serializers.CharField(source="get_case_tag_display")  #默认获取枚举值里面key对应的value值,如{1, "冒烟用例"}
    #tag = serializers.CharField(source="case_tag")

    class Meta:
        model = models.CaseSuit
        fields = '__all__'


class CaseSuitInfoSerializer(serializers.ModelSerializer):
    """
    用例步骤序列化
    """
    body = serializers.SerializerMethodField()

    class Meta:
        model = models.CaseSuitInfo
        fields = ['id', 'case_name','config_name','interface_path', 'method', 'body', 'case_id', 'source_api_id', 'creator', 'updater']
        depth = 1

    def get_body(self, obj):
        body = eval(obj.body)
        if "base_url" in body["request"].keys():
            return {
                "name": body["name"],
                "method": "config"
            }
        if 'ac_name' in body.keys():
            return {
                'ac_name':body['ac_name'],
                'method':'ac_config',
            }
        else:
            parse = Parse(eval(obj.body))
            parse.parse_http()
            return parse.testcase


class APIRelatedCaseSerializer(serializers.Serializer):  #两表关联序列----------------------------------------
    #case_name = serializers.CharField(source='case.name')
    suit_name = serializers.CharField(source='case_name')
    case_id = serializers.CharField(source='id')

    class Meta:
        #fields = ['case_id', 'suit_name']
        fields = '__all__'


class APISerializer(serializers.ModelSerializer):
    """
    接口信息序列化
    """
    body = serializers.SerializerMethodField()
    tag_name = serializers.CharField(source="get_tag_display")
    #tag_name = serializers.CharField(source="case_tag")
    cases = serializers.SerializerMethodField()
    relation_name = serializers.SerializerMethodField()

    class Meta:
        model = models.API
        fields = '__all__'
        # fields = ['id', 'interface_name', 'interface_path', 'method', 'project', 'relation', 'body', 'rig_env', 'tag', 'tag_name',
        #           'update_time', 'delete', 'creator', 'updater', 'cases', 'relation_name']

    def get_body(self, obj):  #序列化时，修改前端传过来值，再返回给request
        parse = Parse(eval(obj.body))
        parse.parse_http()
        return parse.testcase

    def get_cases(self, obj):
        cases = models.CaseSuitInfo.objects.filter(source_api_id=obj.id)
        case_id = APIRelatedCaseSerializer(many=True, instance=cases)
        return case_id.data

    def get_relation_name(self, obj):
        relation_obj = models.Relation.objects.get(project_id=obj.project_id, type=1)
        label = get_tree_relation_name(eval(relation_obj.tree), obj.relation)
        return label

    # def get_cases(self, obj):
    #     cases = obj.api_case_relate.all()
    #     case_id = CaseSerializer(many=True, instance=cases)
    #     return case_id.data


class ConfigSerializer(serializers.ModelSerializer):
    """
    配置信息序列化
    """
    body = serializers.SerializerMethodField()

    class Meta:
        model = models.Config
        fields = ['id', 'base_url', 'body', 'name', 'update_time', 'is_default', 'creator', 'updater']
        depth = 1

    def get_body(self, obj):
        parse = Parse(eval(obj.body), level='config')
        parse.parse_http()
        return parse.testcase


class ReportSerializer(serializers.ModelSerializer):
    """
    报告信息序列化
    """
    type = serializers.CharField(source="get_type_display")
    time = serializers.SerializerMethodField()
    stat = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()
    success = serializers.SerializerMethodField()

    class Meta:
        model = models.Report
        fields = ["id", "name", "type", "time", "stat", "platform", "success", 'creator', 'updater']

    def get_time(self, obj):
        return eval(obj.summary)["time"]

    def get_stat(self, obj):
        return eval(obj.summary)["stat"]

    def get_platform(self, obj):
        return eval(obj.summary)["platform"]

    def get_success(self, obj):
        return eval(obj.summary)["success"]


class VariablesSerializer(serializers.ModelSerializer):
    """
    变量信息序列化
    """
    key = serializers.CharField(allow_null=False, max_length=100, required=True)
    value = serializers.CharField(allow_null=False, max_length=1024)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = models.Variables
        fields = '__all__'


class HostIPSerializer(serializers.ModelSerializer):
    """
    变量信息序列化
    """

    class Meta:
        model = models.HostIP
        fields = '__all__'


class DBConfigSerializer(serializers.ModelSerializer):
    '''
    数据库配置信息序列化
    '''
    db_info=serializers.SerializerMethodField()

    class Meta:
        model = models.DBConfig  #引用DBConfig的字段校验
        fields = '__all__'
        # fields=["db_name","project","description"]

    # def validate(self,attrs):  #对单个、多个字段进行处理
    #     db_info=attrs["db_info"]
    #     if not isinstance(db_info,dict):
    #         raise serializers.ValidationError("数据库配置信息,db_info必须为dict格式")
    #     if isinstance(self.db_info,dict):
    #         attrs["db_info"]=str(dict)
    #     return attrs

    # def validate_db_info(self, value):
    #     if not isinstance(value,dict):
    #         raise serializers.ValidationError('数据库配置信息需为dict')
    #     return value
    def get_db_info(self,obj):
        '''
        获取自定义的db_info字段的值，并返回给响应
        此函数会在list运行完毕后，调用获取db_info的值回填到response中
        '''
        db_info=eval(obj.db_info)
        return db_info


    def db_info_check(self,data):
        if not isinstance(data, dict):
            return "数据库配置信息:db_info必须为dict格式"
        else:
            return


class AccountConfigSeSerializer(serializers.ModelSerializer):

    ac_info = serializers.SerializerMethodField()
    fixture_name=serializers.SerializerMethodField()
    class Meta:
        model=models.AccountConfig
        fields='__all__'

    def get_ac_info(self,obj):
        '''
        获取自定义的ac_info字段的值，并返回给响应
        此函数会在list运行完毕后，调用获取ac_info的值回填到response中,必须要在上面指定这个字段的serializers.SerializerMethodField()，
        才会处理
        '''
        ac_info=eval(obj.ac_info)
        return ac_info

    def get_fixture_name(self,obj):
        fixture_obj=models.Fixture.objects.get(id=obj.fixture_id)
        fixture_name=fixture_obj.name
        return fixture_name

    def ac_info_check(self,data):
        if not isinstance(data, dict):
            return "数据库配置信息:ac_info必须为dict格式"
        else:
            return

class EnvSerializer(serializers.ModelSerializer):
    '''
    环境序列化
    '''
    class Meta:
        model=models.Env
        fields='__all__'


class FixtureSerializer(serializers.ModelSerializer):
    '''
    fixture序列化
    '''
    # id = serializers.CharField(required=False)
    # creatorNickname = serializers.CharField(source="creator_nickname")
    # curProjectId = serializers.CharField(source="project_id")

    class Meta:
        model = models.Fixture
        fields = '__all__'


def get_cron_next_execute_time(crontab_expr: str):
    entry = CronTab(crontab_expr)
    return int(entry.next(default_utc=False)+time.time())


class PeriodicTaskSerializer(serializers.ModelSerializer):
    """
    定时任务信列表序列化
    """
    kwargs = serializers.SerializerMethodField()
    args = serializers.SerializerMethodField()

    class Meta:
        model = celery_models.PeriodicTask
        fields = ['id', 'name', 'args', 'kwargs', 'enabled', 'date_changed', 'enabled', 'description']

    def get_kwargs(self, obj):
        kwargs = json.loads(obj.kwargs)
        if obj.enabled:
            kwargs['next_execute_time'] = get_cron_next_execute_time(kwargs['crontab'])
        return kwargs

    def get_args(self, obj):
        case_id_list = json.loads(obj.args)
        # 数据格式,list of dict : [{"id":case_id,"name":case_name}]
        return list(models.CaseSuit.objects.filter(pk__in=case_id_list).values('id', 'name'))




