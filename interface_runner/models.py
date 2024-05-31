from django.db import models

# Create your models here.
from model_utils import Choices


class BaseTable(models.Model):
    """
    公共字段列
    """

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        app_label = 'interface_runner'

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    creator = models.CharField(verbose_name="创建人", max_length=20, null=True)
    updater = models.CharField(verbose_name="更新人", max_length=20, null=True)


class Project(BaseTable):
    """
    项目信息表
    """

    class Meta:
        verbose_name = "项目信息"
        db_table = "project"

    name = models.CharField("项目名称", unique=True, null=False, max_length=100)  # unique为表中必须为唯一值
    desc = models.CharField("简要介绍", max_length=100, null=False)
    responsible = models.CharField("创建人", max_length=20, null=False)
    yapi_base_url = models.CharField("yapi的openapi url", max_length=100, null=False, default='', blank=True)
    yapi_openapi_token = models.CharField("yapi openapi的token", max_length=128, null=False, default='', blank=True)


class Env(BaseTable):
    '''
    环境信息表
    '''

    class Meta:
        verbose_name = "环境信息"
        db_table = "env"

    name = models.CharField("环境名称", unique=True, null=False, max_length=100)


class Debugtalk(BaseTable):
    """
    驱动文件表
    """

    class Meta:
        verbose_name = "驱动库"
        db_table = "debugtalk"

    code = models.TextField("python代码", default="# write you code", null=False)
    env_id = models.IntegerField("环境id", default=0)
    project = models.OneToOneField(to=Project, on_delete=models.CASCADE, db_constraint=False)


class Config(BaseTable):
    """
    环境信息表
    """

    class Meta:
        verbose_name = "环境信息"
        db_table = "config"

    name = models.CharField("环境名称", null=False, max_length=100)
    body = models.TextField("主体信息", null=False)
    base_url = models.CharField("请求地址", null=False, max_length=100)
    env_id = models.IntegerField("环境id", default=0)
    # ForeignKey为设置为外键，on_delete=models.CASCADE为级联关系，主表数据删除时，外键表的一同删除
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)
    is_default = models.BooleanField("默认配置", default=False)


class API(BaseTable):
    """
    API信息表，用例模板，用这个用例在页面拖动组合成suit
    """

    class Meta:
        verbose_name = "接口信息"
        db_table = "api"

    ENV_TYPE = (
        (0, "测试环境"),
        (1, "灰度环境"),
        (2, "生产环境")
    )

    ORIGIN_TYPE = (
        (0, "手动输入"),
        (1, "excel导入"),
        (2, "ypai导入")
    )
    TAG = Choices(
        (0, "未知"),
        (1, "成功"),
        (2, "失败"),
        (3, "自动成功")
    )
    interface_name = models.CharField("接口名称", null=False, max_length=100, db_index=True)
    method = models.CharField("请求方式", null=False, max_length=10)
    interface_path = models.CharField("请求地址", null=False, max_length=255, db_index=True)
    body = models.TextField("主体信息", null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)
    relation = models.IntegerField("节点id", null=False)
    delete = models.IntegerField("是否删除", null=True, default=0)
    env_id = models.IntegerField("环境id", default=0)
    rig_id = models.IntegerField("网关API_id", null=True, db_index=True)
    rig_env = models.IntegerField("网关环境", choices=ENV_TYPE, default=0)
    tag = models.IntegerField("API标签", choices=TAG, default=0)
    # yapi相关的
    yapi_catid = models.IntegerField("yapi的分组id", null=True, default=0)
    yapi_id = models.IntegerField("yapi的id", null=True, default=0)
    ypai_add_time = models.CharField("yapi创建时间", null=True, default='', max_length=10)
    ypai_up_time = models.CharField("yapi更新时间", null=True, default='', max_length=10)
    ypai_username = models.CharField("yapi的原作者", null=True, default='', max_length=30)
    type = models.IntegerField("数据来源方式", choices=ORIGIN_TYPE, default=0)


class CaseSuit(BaseTable):
    """
    用例信息表,测试套件suit，多条用例组合后的一个组合suit。总预览
    """

    class Meta:
        verbose_name = "用例信息"
        db_table = "case_suit"

    tag = (
        (1, "冒烟用例"),
        (2, "集成用例"),
        (3, "监控脚本")
    )
    suit_name = models.CharField("用例名称", null=False, max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)
    relation = models.IntegerField("节点id", null=False)
    case_count = models.IntegerField("API个数", null=False)
    env_id = models.IntegerField("环境id", default=0)
    case_tag = models.IntegerField("用例标签", choices=tag, default=2)
    # apis = models.ManyToManyField(API, db_table='api_case', related_name='api_case_relate')


class CaseSuitInfo(BaseTable):
    """
    Test Case Step，存储组合用例数据，页面拖动后形成的用例集
    """

    class Meta:
        verbose_name = "用例信息 Step"
        db_table = "case_suit_info"

    ORIGIN_TYPE = (
        (0, "手动输入"),
        (1, "excel导入"),
        (2, "ypai导入")
    )

    case_name = models.CharField("用例名称", null=True, max_length=100)
    config_name = models.CharField("配置名称", null=True, max_length=100)
    body = models.TextField("主体信息", null=False)
    method = models.CharField("请求方式", null=False, max_length=10)
    interface_path = models.CharField("请求地址", null=True, max_length=255)
    # case = models.ForeignKey(CaseSuit, on_delete=models.CASCADE, db_constraint=False)
    env_id = models.IntegerField("环境id", default=0)
    case = models.ForeignKey(CaseSuit, on_delete=models.CASCADE,
                             db_constraint=False)  # ForeignKey表示设置外键，会自己生成id，对应字段名就是case_id
    step = models.IntegerField("顺序", null=False)
    source_api_id = models.IntegerField("api来源", null=False)
    type = models.IntegerField("数据来源方式", choices=ORIGIN_TYPE, default=0)


class HostIP(BaseTable):
    """
    全局变量
    """

    class Meta:
        verbose_name = "HOST配置"
        db_table = "host_ip"

    name = models.CharField(null=False, max_length=100)
    value = models.TextField(null=False)
    env_id = models.IntegerField("环境id", default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)


class Variables(BaseTable):
    """
    全局变量
    """

    class Meta:
        verbose_name = "全局变量"
        db_table = "variables"

    key = models.CharField(null=False, max_length=100)
    value = models.CharField(null=False, max_length=1024)
    env_id = models.IntegerField("环境id", default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)
    description = models.CharField("全局变量描述", null=True, max_length=100)


class Fixture(BaseTable):
    '''
    前置条件fixture
    '''

    class Meta:
        db_table = "fixture"

    name = models.CharField("fixture名称", max_length=100, null=False)
    desc = models.CharField("fixture描述", max_length=500, default="")
    code = models.TextField("代码", max_length=30000, null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)
    env_id = models.IntegerField("环境id", default=0)


class Report(BaseTable):
    """
    报告存储
    """
    report_type = (
        (1, "调试"),
        (2, "异步"),
        (3, "定时"),
        (4, "部署"),
    )
    report_status = (
        (0, "失败"),
        (1, "成功"),
    )

    class Meta:
        verbose_name = "测试报告"
        db_table = "report"

    name = models.CharField("报告名称", null=False, max_length=100)
    type = models.IntegerField("报告类型", choices=report_type)
    status = models.BooleanField("报告状态", choices=report_status, blank=True)
    summary = models.TextField("报告基础信息", null=False)
    env_id = models.IntegerField("环境id", default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)


class ReportDetail(models.Model):
    class Meta:
        verbose_name = "测试报告详情"
        db_table = "report_detail"
        app_label = 'interface_runner'

    report = models.OneToOneField(Report, on_delete=models.CASCADE, null=True, db_constraint=False)
    summary_detail = models.TextField("报告详细信息")
    env_id = models.IntegerField("环境id", default=0)


class Relation(models.Model):
    """
    树形结构关系
    """

    class Meta:
        verbose_name = "树形结构关系"
        db_table = "relation"
        app_label = 'interface_runner'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)
    tree = models.TextField("结构主题", null=False, default=[])
    env_id = models.IntegerField("环境id", default=0)
    type = models.IntegerField("树类型", default=1)


class Visit(models.Model):
    METHODS = Choices(
        ('GET', "GET"),
        ('POST', "POST"),
        ('PUT', "PUT"),
        ('PATCH', "PATCH"),
        ('DELETE', "DELETE"),
        ('OPTION', "OPTION"),
    )

    user = models.CharField(max_length=100, verbose_name='访问url的用户名', db_index=True)
    ip = models.CharField(max_length=20, verbose_name='用户的ip', db_index=True)
    project = models.CharField(max_length=4, verbose_name='项目id', db_index=True, default=0)
    url = models.CharField(max_length=255, verbose_name='被访问的url', db_index=True)
    path = models.CharField(max_length=100, verbose_name='被访问的接口路径', default='', db_index=True)
    request_params = models.CharField(max_length=255, verbose_name='请求参数', default='', db_index=True)
    request_method = models.CharField(max_length=7, verbose_name='请求方法', choices=METHODS, db_index=True)
    request_body = models.TextField(verbose_name='请求体')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, db_index=True)
    env_id = models.IntegerField("环境id", default=0)

    class Meta:
        db_table = 'visit'
        app_label = 'interface_runner'


class DBConfig(BaseTable):
    class Meta:
        verbose_name = "数据库配置"
        db_table = "db_config"

    db_name = models.CharField("数据库名", null=False, max_length=100)
    db_info = models.TextField("数据库配置信息", null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)
    description = models.CharField("数据库描述", null=True, max_length=100)
    env_id = models.IntegerField("环境id", default=0)


class AccountConfig(BaseTable):
    class Meta:
        verbose_name = "账号配置"
        db_table = "ac_config"

    ac_name = models.CharField("账号名", null=False, max_length=100)
    ac_info = models.TextField("账号配置信息", null=False)
    fixture_id = models.IntegerField("fixture id", null=True, )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_constraint=False)
    description = models.CharField("账号描述", null=True, max_length=100)
    env_id = models.IntegerField("环境id", default=0)
