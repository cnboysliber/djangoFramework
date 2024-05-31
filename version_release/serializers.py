from django.db import models
from rest_framework import serializers
from .models import SeviceListTable,VersionManage,VersionUATManage,BusinessLineManage,ProductLineManage,GitProData,GitProgrammeData,RaiseOtherData,BaseRaiseInfo,SitConfigList,SitOtherConfigData,sitFileList,sitOtherFileList,sitAssemblyList,UatRaiseInfo,UatAssemblyList,AccompanyTestList,AccompanyListData



class SeviceListTableModelSerializer(serializers.ModelSerializer):
    """
    服务列表序列化
    """
    class Meta:
        model = SeviceListTable
        fields = "__all__"


class VersionManageSerializer(serializers.ModelSerializer):
    """
    SIT版本提测序列化
    """
    class Meta:
        model = VersionManage
        fields = "__all__"
        # fields=['function_name','project_name','assembly_name','service_list','business_line','product_line','raise_test',]


class VersionUATManageSerializer(serializers.ModelSerializer):
    """
    UAT版本提测序列化
    """
    class Meta:
        model = VersionUATManage
        fields = "__all__"


class BusinessSerializer(serializers.ModelSerializer):
    """
    业务线
    """
    class Meta:
        model = BusinessLineManage
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """
    业务线
    """
    class Meta:
        model = ProductLineManage
        fields = "__all__"


class GitProjectDataSerializer(serializers.ModelSerializer):
    """
    获取git项目数据
    """
    class Meta:
        model = GitProData
        fields = "__all__"

class GitProgrameSerializer(serializers.ModelSerializer):
    """
    根据工程名获取对应项目组件名
    """
    class Meta:
        model = GitProgrammeData
        fields = "__all__"


class RaiseOtherDataSerializer(serializers.ModelSerializer):
    """
    其他提测内容
    """
    class Meta:
        model = RaiseOtherData
        fields = "__all__"


class BaseRaiseInfoSerializer(serializers.ModelSerializer):
    """
    提测基本内容
    """


    class Meta:
        model = BaseRaiseInfo
        fields = "__all__"


class SitConfigListSerializer(serializers.ModelSerializer):
    """
    提测内容
    """

    class Meta:
        model = SitConfigList
        fields = "__all__"


class SitOtherConfigDataSerializer(serializers.ModelSerializer):
    """
    其他提测内容
    """
    class Meta:
        model = SitOtherConfigData
        fields = "__all__"


class SitFileListSerializer(serializers.ModelSerializer):
    """
    脚本内容
    """
    class Meta:
        model = sitFileList
        fields = "__all__"


class SitOtherFileListSerializer(serializers.ModelSerializer):
    """
    其他脚本内容
    """
    class Meta:
        model = sitOtherFileList
        fields = "__all__"


class sitAssemblyFileSerializer(serializers.ModelSerializer):
    """
    组件提测内容
    """
    # system_name = serializers.SerializerMethodField(read_only=True)
    # level = serializers.SerializerMethodField(read_only=True)
    # raise_label = serializers.SerializerMethodField(read_only=True)
    # raise_env = serializers.SerializerMethodField(read_only=True)
    # pro_name = serializers.SerializerMethodField(read_only=True)
    # raise_time = serializers.SerializerMethodField(read_only=True)
    # raise_people = serializers.SerializerMethodField(read_only=True)
    # program_status = serializers.SerializerMethodField(read_only=True)
    # raiseID = serializers.SerializerMethodField(read_only=True)
    # raiseCommitID = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = sitAssemblyList
        fields = "__all__"

    # @staticmethod
    # def get_system_name(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.system_name
    #
    # @staticmethod
    # def get_level(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.level
    #
    # @staticmethod
    # def get_raise_label(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raise_label
    #
    # @staticmethod
    # def get_raise_env(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raise_env
    #
    # @staticmethod
    # def get_pro_name(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.pro_name
    #
    # @staticmethod
    # def get_raise_time(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raise_time
    #
    # @staticmethod
    # def get_raise_people(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raise_people
    #
    # @staticmethod
    # def get_program_status(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.program_status
    #
    # @staticmethod
    # def get_raiseID(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raiseID
    #
    # @staticmethod
    # def get_raiseCommitID(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raiseCommitID


class UatRaiseInfoSerializer(serializers.ModelSerializer):
    """
    uat提测内容
    """
    # system_name = serializers.SerializerMethodField(read_only=True)
    # level = serializers.SerializerMethodField(read_only=True)
    # raise_label = serializers.SerializerMethodField(read_only=True)
    # raise_env = serializers.SerializerMethodField(read_only=True)
    # pro_name = serializers.SerializerMethodField(read_only=True)
    # raise_time = serializers.SerializerMethodField(read_only=True)
    # raise_people = serializers.SerializerMethodField(read_only=True)
    # program_status = serializers.SerializerMethodField(read_only=True)
    # raiseID = serializers.SerializerMethodField(read_only=True)
    # raiseCommitID = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UatRaiseInfo
        fields = "__all__"

    # @staticmethod
    # def get_system_name(obj):
    #     system_name = BaseRaiseInfo.objects.get(id=obj.project_id).system_name
    #     return system_name
    #
    # @staticmethod
    # def get_level(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.level
    #
    # @staticmethod
    # def get_raise_label(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raise_label
    #
    # @staticmethod
    # def get_raise_env(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raise_env
    #
    # @staticmethod
    # def get_pro_name(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.pro_name
    #
    # @staticmethod
    # def get_raise_time(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raise_time
    #
    # @staticmethod
    # def get_raise_people(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raise_people
    #
    # @staticmethod
    # def get_program_status(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.program_status
    # @staticmethod
    # def get_raiseID(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raiseID
    #
    # @staticmethod
    # def get_raiseCommitID(obj):
    #     query = BaseRaiseInfo.objects.filter(id=obj.project_id).first()
    #     return query.raiseCommitID


class UatAssemblyListSerializer(serializers.ModelSerializer):
    """
    其他脚本内容
    """
    class Meta:
        model = UatAssemblyList
        fields = "__all__"


class AccompanyProductsSerializer(serializers.ModelSerializer):
    """
    陪测产品列表
    """
    class Meta:
        model = AccompanyTestList
        fields = "__all__"


class AccompanyListDataSerializer(serializers.ModelSerializer):
    """
    陪测产品列表详细信息
    """
    class Meta:
        model = AccompanyListData
        fields = "__all__"
