from django.db import models


class BaseTable(models.Model):
    """
    公共字段列
    """

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        app_label = 'mock'


class ApiMock(BaseTable):
    """
    MOCK映射表
    """
    class Mata:
        verbose_name = "MOCK映射表"
        db_table = "api_mock"

    apiEnv = models.CharField('环境地址',max_length=255, null=False)
    apiName = models.CharField('接口名称',max_length=255, null=False)
    expectName = models.CharField('判定参数',max_length=255, null=False)
    expectValue = models.CharField('判定值',max_length=255, null=False)
    respHeaders = models.CharField(max_length=1000, null=False, default='{}')
    respData = models.TextField('返回内容',null=False)
    respStatusCode = models.IntegerField('返回设置',null=False, default=200)
    fileName = models.CharField('文件名',max_length=64, null=True)
    status = models.SmallIntegerField(default=1)
    createTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)


class ConditionMockRes(BaseTable):
    """
    条件返回值
    """

    class Mata:
        verbose_name = "条件返回值"
        db_table = "condition_mockRes"

    mockId = models.IntegerField(help_text='关联的mockId')
    condition = models.CharField('判断条件',max_length=255, null=True)
    respData = models.TextField('返回内容',null=False)
    respStatusCode = models.IntegerField('返回码',null=False, default=200)
    status = models.SmallIntegerField(default=1)
    createTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)