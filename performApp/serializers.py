import os
from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from performApp import models
from performApp.utils import common, jmeterApi
from FasterRunner.utils.logging import logger


User = get_user_model()


class BaseSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    updater = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    real_name = serializers.SerializerMethodField(read_only=True)

    def save(self, **kwargs):
        """Include default for read_only `user` field"""
        kwargs["creator"] = self.fields["creator"].get_default()
        kwargs["updater"] = self.fields["updater"].get_default()
        return super().save(**kwargs)

    @staticmethod
    def get_real_name(obj):
        if obj.creator == 'admin':
            return obj.creator

        real_name = User.objects.get(username=obj.creator).first_name
        return real_name


class PerformReportSerializer(serializers.ModelSerializer):
    """
    压测报告序列化
    """
    err_rate = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    ptype_name = serializers.SerializerMethodField()
    tps = serializers.SerializerMethodField()

    class Meta:
        model = models.PerformReport
        fields = '__all__'

    @staticmethod
    def get_tps(obj):
        return obj.tps / 100 if obj.tps else 0

    @staticmethod
    def get_err_rate(obj):
        return (obj.err_rate or 0) / 100.0

    @staticmethod
    def get_item_name(obj):
        return obj.get_item_display()

    @staticmethod
    def get_ptype_name(obj):
        return obj.get_ptype_display()

    @staticmethod
    def get_date(dates):  # 定义转化日期戳的函数,dates为日期戳
        delta = timedelta(days=dates)
        today = datetime.strptime('1899/12/30', '%Y/%m/%d') + delta  # 将1899-12-30转化为可以计算的时间格式并加上要转化的日期戳
        return datetime.strftime(today, '%Y-%m-%d')


class PerformProjectSerializer(BaseSerializer):
    """
    压测报告序列化
    """
    err_rate = serializers.SerializerMethodField()

    class Meta:
        model = models.PerformProject
        fields = '__all__'

    @staticmethod
    def get_err_rate(obj):
        return (obj.err_rate or 0) / 100.0


class TestTypeSerializer(BaseSerializer):
    """
    测试类型序列化
    """
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = models.TestType
        fields = '__all__'


class ScenesManageSerializer(BaseSerializer):
    """
    场景管理序列化
    """
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    state = serializers.SerializerMethodField(read_only=True)
    schedule = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ScenesManage
        fields = '__all__'

    @staticmethod
    def get_update_info(request):  # add接口加入用户信息
        return common.get_user_info(request)

    @staticmethod
    def get_state(obj):
        scene_uid = obj.scene_uid
        try:
            jmt = jmeterApi.JmRest()
            data = jmt.get_scene_detail(scene_uid)
            state = data.get('status')
        except Exception as e:
            logger.error('scene state query error:{}'.format(str(e)))
            state = ''
        return state

    @staticmethod
    def get_schedule(obj):
        """
        获取定时任务信息
        :param obj:
        :return:
        """
        task = models.ApiPerformancePlan.objects.filter(scene_id=obj.id, status=1).first()
        if not task:
            return '否'
        info = '|'.join([task.get_plan_type_display(), task.plan_time])
        return info


class PerformEnvSerializer(BaseSerializer):
    """
    压测环境管理信息
    """

    class Meta:
        model = models.PerformEnv
        fields = '__all__'


class ServicesServerSerializer(BaseSerializer):
    """
    压测环境对应的服务器信息
    """

    class Meta:
        model = models.ServicesServer
        fields = '__all__'


class PerformScriptSerializer(BaseSerializer):
    """
    压测报告序列化
    """

    class Meta:
        model = models.PerformScript
        fields = '__all__'


class PerformScriptParamsSerializer(serializers.ModelSerializer):
    """
    压测参数化文件
    """

    class Meta:
        model = models.PerformScriptParams
        fields = '__all__'


class BugsSerializer(serializers.ModelSerializer):
    """
    bugs序列化
    """
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    project_name = serializers.SerializerMethodField(read_only=True)
    version = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Bugs
        fields = '__all__'

    @staticmethod
    def get_version(obj):
        query = models.PerformProject.objects.filter(id=obj.project_id, status=1).first()
        return query.version

    @staticmethod
    def get_project_name(obj):
        query = models.PerformProject.objects.filter(id=obj.project_id, status=1).first()
        return query.project

    @staticmethod
    def get_update_info(obj):  # add接口加入用户信息
        return common.get_user_info(obj)


class PerformServerSerializer(serializers.ModelSerializer):
    """
    压测机信息序列化
    """
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = models.PerformServer
        fields = '__all__'

    @staticmethod
    def get_update_info(request):  # add接口加入用户信息
        return common.get_user_info(request)


class ApiPerformancePlanSerializer(BaseSerializer):
    """
    压测报告序列化
    """

    class Meta:
        model = models.ApiPerformancePlan
        fields = '__all__'


class JacocoServiceSerializer(serializers.ModelSerializer):
    """
    Jacoco服务序列化
    """

    class Meta:
        model = models.JacocoService
        fields = '__all__'


class JacocoTaskSerializer(serializers.ModelSerializer):
    """
    Jacoco任务序列化
    """
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = models.JacocoTask
        fields = '__all__'
