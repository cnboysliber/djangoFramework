from rest_framework import serializers
from .models import UploadOrganization,UploadOrganizationData,GitCommitData
from .models import UploadOrganization, UploadOrganizationData, MonthVersion, Version, ChildVersion
from quality_management.utils import common


class UploadOrganizationSerializer(serializers.ModelSerializer):
    """
    上传组织架构文件信息
    """
    class Meta:
        model = UploadOrganization
        fields = "__all__"


class UploadOrganizationDataSerializer(serializers.ModelSerializer):
    """
    上传组织架构文件数据信息
    """
    class Meta:
        model = UploadOrganizationData
        fields = "__all__"


class MonthVersionSerializer(serializers.ModelSerializer):
    """
    月版本数据信息
    """

    class Meta:
        model = MonthVersion
        fields = "__all__"

    @staticmethod
    def get_login_info(obj):  # add接口加入用户信息
        return common.get_user_info(obj)




class VersionSerializer(serializers.ModelSerializer):
    """
    大版本数据信息
    """

    class Meta:
        model = Version
        fields = "__all__"

    @staticmethod
    def get_login_info(obj):  # add接口加入用户信息
        return common.get_user_info(obj)

class ChildVersionSerializer(serializers.ModelSerializer):
    """
    小版本数据信息
    """

    class Meta:
        model = ChildVersion
        fields = "__all__"

    @staticmethod
    def get_login_info(obj):  # add接口加入用户信息
        return common.get_user_info(obj)


class GitCommitDataSerializer(serializers.ModelSerializer):
    """
    git代码量提交数据
    """
    class Meta:
        model = GitCommitData
        fields = "__all__"
