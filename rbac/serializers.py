import os
from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from performApp import models
from performApp.utils import common, jmeterApi
from rest_framework import serializers
from .models import Role, ParentMenu,ChildMenu

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    """
    角色 序列化
    """

    class Meta:
        model = Role
        fields = "__all__"


class ParentMenuSerializer(serializers.ModelSerializer):
    """
    父菜单列表序列化
    """

    class Meta:
        model = ParentMenu
        fields = "__all__"


class ChildMenuSerializer(serializers.ModelSerializer):
    """
    子菜单列表序列化
    """

    class Meta:
        model = ChildMenu
        fields = "__all__"

