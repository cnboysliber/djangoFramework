import time
from django.db import models
# Create your models here.
from model_utils import Choices
from datetime import datetime,date


class BaseTable(models.Model):
    """
    公共字段列
    """
    status = models.SmallIntegerField(verbose_name='逻辑状态', default=1, null=False)

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        app_label = 'quality_management'

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    creator = models.CharField(verbose_name="创建人", max_length=20, null=True)
    updater = models.CharField(verbose_name="更新人", max_length=20, null=True)


class UploadOrganization(BaseTable):
    """
    文件上传
    """

    class Meta:
        verbose_name = "组织架构文件"
        db_table = "organization_table"

    organization_file = models.FileField(blank=True, null=False)
    title = models.CharField(max_length=50)
    timestamp = models.DateTimeField('上传时间', default=datetime.now)


class UploadOrganizationData(BaseTable):
    """
    组织架构详细数据
    """

    class Meta:
        verbose_name = "组织架构详细数据"
        db_table = "org_data_table"

    name = models.CharField('姓名', max_length=20)
    job = models.CharField('岗位', max_length=20, null=True)
    business_line = models.CharField('业务线', max_length=20, null=True)
    person_type = models.CharField('人员类型', max_length=20, null=True)
    develop_group = models.CharField('开发组', max_length=20, null=True)
    skill_name = models.CharField('技术栈', max_length=20, null=True)
    person_state = models.CharField('人员状态', max_length=20, null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据
    upload_time = models.DateField('上传默认时间', default=datetime.now)
    ems=models.CharField('ems账号', max_length=20, null=True)
    workspace=models.CharField('工作地点', max_length=20, null=True)


class GitCommitData(BaseTable):
    """
    代码量提交数据
    """

    class Meta:
        verbose_name = "代码量提交数据"
        db_table = "git_commit_table"

    git_project_id = models.CharField('项目ID', max_length=20)
    project_name = models.CharField('项目名称', max_length=50, null=True)
    branch = models.CharField('项目分支', max_length=50, null=True)
    commit_id = models.CharField('Commit_ID', max_length=200, null=True)
    title = models.CharField('标题', max_length=1000, null=True)
    message = models.CharField('标题', max_length=1000, null=True)
    git_type = models.CharField('提交类型', max_length=20, null=True)
    author_name = models.CharField('提交人员', max_length=20, null=True)
    committed_date = models.CharField(verbose_name='提交日期', max_length=50, null=True)
    additions = models.CharField('新增行数', max_length=50, null=True)
    deletions = models.CharField('删除行数', max_length=50, null=True)
    total = models.IntegerField('总变化行数', null=True)


class MonthVersion(BaseTable):
    """
    版本/用例
    """

    class Meta:
        db_table = 'month_version'

    TYPES = Choices(
        (1, '测试版本'),
        (2, '测试用例'),
    )

    type = models.SmallIntegerField(verbose_name='版本/用例', choices=TYPES)
    year_month = models.CharField(verbose_name="年月", max_length=20, default='')

class Version(BaseTable):
    """
    月份版本
    """

    class Meta:
        db_table = 'version'

    month_version_id = models.SmallIntegerField(verbose_name="月份版本ID")
    name = models.CharField(verbose_name='版本名称', max_length=50, default='')

class ChildVersion(BaseTable):
    """
    月份子版本
    """

    class Meta:
        db_table = 'child_version'

    version_id = models.SmallIntegerField(verbose_name="版本ID")
    system_name = models.CharField(verbose_name='系统名称', max_length=50, default='')
    version_num = models.CharField(verbose_name='版本号', max_length=20, default='')
