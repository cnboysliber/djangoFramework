# -*- coding: utf-8 -*-
import os
import json
import xlrd
import shutil
from xlrd import xldate_as_tuple
from datetime import datetime
from loguru import logger
from django.db.models import Count
from version_release.utils import day

from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser

from FasterRunner import pagination
from FasterRunner import const as cnt
from version_release import models
from version_release import serializers
from version_release.utils import response
from FasterRunner.utils.decorator import request_log
from version_release.views.sit_base_info import BaseRaiseInfoView
from version_release.views.sit_raise_info import SitRaiseInfoView


class DelInfoView(GenericViewSet):
    """
    sit提测删除功能
    """
    queryset_base = models.BaseRaiseInfo.objects.all()
    queryset_ass = models.sitAssemblyList.objects.all()
    serializer_class = serializers.sitAssemblyFileSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        perform-单个删除提测记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(response.PERFORM_AUTH_PERMISSIONS)
        try:
            checkData=self.queryset_ass.filter(id=kwargs['pk']).first()
            serializer = self.get_serializer(checkData)
            num=json.loads(json.dumps(serializer.data))
            # self.queryset_base.filter(id=num['project']).update(status=cnt.NOT_ACTIVE)
            self.queryset_ass.filter(project=num['project']).update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)


class SearchInfoView(GenericViewSet):
    """
    sit搜搜功能
    """
    queryset_base = models.BaseRaiseInfo.objects.all()
    queryset_ass = models.sitAssemblyList.objects.all()
    serializer_class = serializers.sitAssemblyFileSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        perform-单个删除提测记录

        :param request:
        :return:
        """
        # checkData=self.queryset_ass.filter(id=kwargs['pk']).first()
        # serializer = self.get_serializer(checkData)
        # num=json.loads(json.dumps(serializer.data))
        # self.queryset_base.filter(id=num['project']).update(status=cnt.NOT_ACTIVE)
        # self.queryset_ass.filter(project=num['project']).update(status=cnt.NOT_ACTIVE)
        pass