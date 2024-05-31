from django.db import models
from rest_framework import serializers
from .models import ConditionMockRes,ApiMock


class ApiMockModelSerializer(serializers.ModelSerializer):
    """
    MOCK映射表
    """
    class Meta:
        model = ApiMock
        fields = "__all__"


class ConditionMockResSerializer(serializers.ModelSerializer):
    """
    条件返回值
    """
    class Meta:
        model = ConditionMockRes
        fields = "__all__"
