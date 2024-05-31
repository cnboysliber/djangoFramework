# -*- coding: utf-8 -*-
import json
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from FasterRunner import pagination
from rbac import models
from rbac import serializers
from FasterRunner.utils.decorator import request_log


class ParentMenuProductsView(GenericViewSet):
    """
    获取获取业务线
    """
    queryset = models.ParentMenu.objects.all()
    serializer_class = serializers.ParentMenuSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='DEBUG'))
    def list(self, request):
        """
        查询服务列表

        :param request:
        :return:
        """
        if request.user.is_superuser:
            from django.core import serializers
            data = json.loads(serializers.serialize('json', models.Role.objects.filter(id=1, status=1).all()))
            permission_data = data[0]['fields']['permissions']
        elif request.user.is_staff and not request.user.is_superuser:
            from django.core import serializers
            data = json.loads(serializers.serialize('json', models.Role.objects.all().filter(id=2, status=1)))
            permission_data = data[0]['fields']['permissions']
        else:
            from django.core import serializers
            data = json.loads(serializers.serialize('json', models.Role.objects.all().filter(id=3, status=1)))
            permission_data = data[0]['fields']['permissions']
        list_count = []
        for per_id in range(len(permission_data)):
            per_data = models.ParentMenu.objects.all().filter(id=permission_data[per_id], status=1).first()
            list_count.append(per_data)
        from django.core import serializers
        data_list = json.loads(serializers.serialize('json', list_count))
        fields_list = []
        for m in range(len(data_list)):
            fields_list.append(data_list[m]['fields'])
        for i in range(len(permission_data)):
            child_data = models.ChildMenu.objects.all().filter(pid_id=permission_data[i], status=1).order_by('order_id')
            serializer = self.get_serializer(child_data, many=True)
            fields_list[i]['class'] = fields_list[i]['icon']
            fields_list[i].pop('icon')
            fields_list[i].pop('path')
            child_list = json.loads(json.dumps(serializer.data))
            for j in range(len(child_list)):
                child_list[j]['code'] = child_list[j]['icon']
                child_list[j]['class'] = child_list[j]['path']
                child_list[j].pop('icon')
                child_list[j].pop('path')
            fields_list[i]['children'] = child_list
        return Response(fields_list)
