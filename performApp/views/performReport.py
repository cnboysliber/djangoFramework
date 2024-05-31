# -*- coding: utf-8 -*-
import os
import xlrd
import traceback
import shutil
from xlrd import xldate_as_tuple
from datetime import datetime
from loguru import logger

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
from performApp import models
from performApp import serializers
from performApp.utils import response
from FasterRunner.utils.command import ShellClient
from FasterRunner.utils.decorator import request_log


class PerformReportView(GenericViewSet):
    """
    performReport-性能报告增删改查
    """
    queryset = models.PerformReport.objects
    serializer_class = serializers.PerformReportSerializer
    pagination_class = pagination.MyPageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(request_log(level='INFO'))
    def list(self, request):
        """
        performReport-查询报告列表

        :param request:
        :return:
        """
        filters = dict({})
        if request.query_params.get('api_env'):
            filters['api_env__in'] = request.query_params.get('api_env')
        filters['api_name__contains'] = request.query_params.get('api_name', '')
        filters['api_url__contains'] = request.query_params.get("api_url", '')
        filters['module__contains'] = request.query_params.get("module", '')
        filters['component__contains'] = request.query_params.get("component", '')
        filters['api_version__contains'] = request.query_params.get("api_version", '')
        filters['manage_name__contains'] = request.query_params.get('manage_name', '')
        if request.query_params.get('item'):
            filters['item__in'] = request.query_params.get('item')
        keyword = request.query_params.get("keyword", '')
        queryset = self.queryset.filter(status=cnt.ACTIVE).order_by('-create_time')
        if request.query_params != '':
            queryset = queryset.filter(Q(api_name__contains=keyword) |
                                       Q(api_url__contains=keyword) |
                                       Q(module__contains=keyword) |
                                       Q(component__contains=keyword) |
                                       Q(api_version__contains=keyword))\
                .filter(**filters)
        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_detail(self, request, **kwargs):
        """
        performReport-查询报告详情

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        queryset = self.queryset.filter(id=pk, status=cnt.ACTIVE).first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    @method_decorator(request_log(level='INFO'))
    def add(self, request):
        """
        performReport-添加性能报告

        :param request:
        :return:
        """

        # 反序列化
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(response.PERFORM_ADD_SUCCESS)
        logger.error(serializer.errors)
        ret = response.SYSTEM_ERROR
        ret.update({'msg': serializer.errors})
        return Response(ret)

    @method_decorator(request_log(level='INFO'))
    def single_delete(self, request, **kwargs):
        """
        performReport-单个删除报告记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id=kwargs['pk']).update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def multi_delete(self, request, **kwargs):
        """
        performReport-批量删除报告记录

        :param request:
        :return:
        """
        if request.user.is_superuser is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            self.queryset.filter(id__in=list(map(lambda x: int(x), request.query_params.values()))) \
                .update(status=cnt.NOT_ACTIVE)
            return Response(response.PERFORM_DELETE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def modify(self, request, **kwargs):
        """
        performReport-更新性能报告

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        try:
            update_kw = {k: v[0] for k, v in dict(request.data).items()}
            self.queryset.filter(id=pk).update(**update_kw)
            return Response(response.PERFORM_UPDATE_SUCCESS)
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level='INFO'))
    def upload_excel(self, request):
        """
        performReport-性能报告导入

        :param request:
        :return:
        """
        resp = response.PERFORM_UPLOAD_SUCCESS
        file = request.FILES['file']
        if not (file.name.endswith('.xls') or file.name.endswith('.xlsx')):
            return Response(response.PERFORM_TYPE_ERROR)
        content = file.read()
        wb = xlrd.open_workbook(file_contents=content)
        sht = wb.sheet_by_index(0)
        headers = ['api_env', 'sys_version', 'api_version', 'ptype', 'item', 'module', 'manage_name',
                   'api_index', 'api_name', 'api_url', 'component', 'req_count', 'resp_ms_90',
                   'resp_ms_99', 'err_rate', 'tps', 'req_time', 'req_period', 'result']
        headers = headers[: len(sht.row_values(0))]
        perform_data = dict({})
        env = {1: 'uat', 2: 'uat2', 3: 'pro'}
        items = {'B端': 1, 'C端': 2, '小程序': 3, 'pc': 4, 'H5': 5, 'SAAS': 6, 'H5_mbrand': 7, '车盟宝小程序': 8, '其他': 20}
        model_data = []
        index = 0
        value = ''
        header_list = sht.row_values(0)
        for row in range(1, sht.nrows):
            cells = sht.row_values(row)
            try:
                for index, value in enumerate(cells):
                    logger.debug('行：{},列:{}，列值：{}'.format(row + 1, index + 1, value))
                    if not value and row != 1:
                        perform_data[headers[index]] = value or sht.row_values(row - 1)[index] or perform_data[headers[index]]
                        value = value or sht.row_values(row - 1)[index]
                    else:
                        perform_data[headers[index]] = value.strip() if isinstance(value, str) else value

                    if headers[index] in ['api_index', 'req_count', 'resp_ms_90', 'resp_ms_99']:
                        perform_data[headers[index]] = int(perform_data[headers[index]]) \
                            if perform_data[headers[index]] and perform_data[headers[index]] != '-' else None
                    elif headers[index] == 'err_rate':
                        perform_data[headers[index]] = int(float(value) * 10000)
                    elif headers[index] == 'tps':
                        perform_data[headers[index]] = int(float(perform_data[headers[index]]) * 100) \
                            if perform_data[headers[index]] and perform_data[headers[index]] != '-' else None

                    elif headers[index] == 'req_time':
                        if value:
                            perform_data[headers[index]] = datetime(*xldate_as_tuple(value, 0)).strftime('%Y-%m-%d')
                        elif isinstance(perform_data[headers[index]], (float, int)):
                            perform_data[headers[index]] = datetime(*xldate_as_tuple(perform_data[headers[index]]
                                                                                     , 0)).strftime('%Y-%m-%d')
                    if index == 0 and value:
                        for k, v in env.items():
                            if v == value.replace('\n', '').strip().lower():
                                perform_data[headers[index]] = k

                    elif index == 3 and value:
                        value = 2 if value.strip() == '混压' \
                            else 1
                        perform_data[headers[index]] = value
                    elif index == 4 and value.strip():
                        perform_data[headers[index]] = items.get(value.strip()) or items.get('其他')
                print(1111111111, perform_data)
                model_data.append(models.PerformReport(**perform_data))
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error('行：{},列:{}，{}, 列值：{}, 异常'.format(row + 1, index + 1, header_list[index], value))
                resp = response.PERFORM_UPLOAD_ERROR
                resp['msg'] = '行：{},列:{}，{}, 列值：{}, 异常:{}'.format(row + 1, index + 1, header_list[index], value, str(e))
                return Response(resp)
        try:
            models.PerformReport.objects.bulk_create(model_data)
        except Exception as e:
            logger.error('插入数据异常：{}'.format(str(e)))
            logger.error(traceback.format_exc())
            resp = response.PERFORM_UPLOAD_ERROR
            resp['msg'] = str(e)
            return Response(resp)
        return Response(resp)

    @method_decorator(request_log(level='INFO'))
    def upload_jtl(self, request, **kwargs):
        """
        performReport-报告jtl导入

        :param request:
        :return:
        """
        pk = kwargs.get('pk')
        file = request.FILES['file']
        if not file.name.endswith('.jtl'):
            return Response(response.PERFORM_TYPE_ERROR)

        content = file.read()
        jmt_dir = os.path.join(settings.JMT_PATH, 'report_{}'.format(pk))
        jtl_dir = os.path.join(settings.JMT_PATH, 'jtl')
        jtl_path = os.path.join(jtl_dir, 'jmt-{}.jtl'.format(pk))
        if not os.path.exists(jtl_dir):
            os.makedirs(jtl_dir)
        if os.path.exists(jmt_dir):
            shutil.rmtree(jmt_dir)
        # 保存jtl文件
        with open(jtl_path, 'wb') as fp:
            fp.write(content)

        cmd = 'jmeter -g {jtl_path} -o {report_path}/ && chown -R nginx {report_path} && rm -rf {jtl_path}'\
            .format(jtl_path=jtl_path, report_path=jmt_dir)
        try:
            ShellClient.execute(cmd)
            if os.path.exists(jmt_dir):
                self.queryset.filter(id=pk).update(result='done')
            else:
                raise
        except Exception as e:
            logger.error('上传jtl文件失败：{}'.format(e))
            return Response(response.PERFORM_UPLOAD_EXE_ERROR)

        return Response(response.PERFORM_UPLOAD_SUCCESS)

    @method_decorator(request_log(level='INFO'))
    def report_exist(self, request, **kwargs):
        """
        performReport-报告是否存在

        :param request:
        :return:
        """
        pk = request.data.get('id')

        jmt_dir = os.path.join(settings.JMT_PATH, 'report_{}'.format(pk))
        if os.path.exists(jmt_dir):
            return Response(response.PERFORM_REPORT_EXIST)
        return Response(response.PERFORM_REPORT_EMPTY)




