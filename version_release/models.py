from django.db import models
# Create your models here.
from model_utils import Choices
from datetime import datetime


class BaseTable(models.Model):
    """
    公共字段列
    """

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        app_label = 'version_release'


class SeviceListTable(BaseTable):
    """
    服务列表
    """

    class Mata:
        verbose_name = "项目信息"
        db_table = "service_table"

    business_line = models.CharField('业务线', max_length=100, db_index=True, null=True)
    product_line = models.CharField('产品线', max_length=100, db_index=True, null=True)
    assembly_name = models.CharField('组件名称', max_length=100, db_index=True, null=True)
    function_name = models.CharField('功能名称', max_length=100, db_index=True, null=True)
    project_name = models.CharField('工程名称', max_length=100, db_index=True, null=True)
    branch = models.CharField('分支', max_length=100, db_index=True, null=True)
    tag = models.CharField('Tag', max_length=100, default='无tag标签')
    develop_man = models.CharField('开发维护人', db_index=True, max_length=20, null=True)
    test_man = models.CharField('测试维护人', max_length=20, db_index=True, null=True)
    git_path = models.CharField('git路径', max_length=100, null=True)
    product_version_now = models.CharField('当前生产版本', max_length=30, null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)
    create_time = models.DateField('申请时间', default=datetime.now)


class VersionManage(BaseTable):
    """
    SIT版本提测
    """

    class Mata:
        verbose_name = "版本提测信息"
        db_table = "version_manage"

    ENV = Choices(
        ('SIT', 'SIT'),
        ('UAT', 'UAT')
    )
    STATUESDATA = Choices(
        ('1', '待审核'),
        ('2', '审核通过，发布UAT'),
        ('3', '已发布UAT')
    )

    function_name = models.CharField('功能名称', max_length=100, db_index=True, null=True)
    project_name = models.CharField('工程名称', max_length=100, db_index=True, null=True)
    assembly_name = models.CharField('组件名称', max_length=100, db_index=True, null=True)
    service_list = models.CharField('服务列表', max_length=100, db_index=True, null=True)
    business_line = models.CharField('业务线', max_length=100, db_index=True, null=True)
    product_line = models.CharField('产品线', max_length=100, db_index=True, null=True)
    raise_test = models.CharField('提测sql脚本', max_length=100, db_index=True, null=True)
    sql_name = models.CharField('sql名称', max_length=100, db_index=True, null=True)
    sql_git_path = models.CharField('sql_git路径', max_length=100, db_index=True, null=True)
    raise_config_file = models.CharField('提测配置文件', max_length=20, db_index=True, null=True)
    service_name = models.CharField('服务名', max_length=100, db_index=True, null=True)
    public_config_path = models.CharField('公共配置', max_length=100, db_index=True, null=True)
    config_file_path = models.CharField('配置文件路径', max_length=100, db_index=True, null=True)
    develop_man = models.CharField('开发维护人', db_index=True, max_length=50, null=True)
    test_man = models.CharField('测试维护人', max_length=50, db_index=True, null=True)
    assemble_commit_id = models.CharField('组件提测commitID', max_length=100, null=True)
    commitId = models.CharField('提测commitID', max_length=100, null=True)
    product_version_now = models.CharField('版本号', max_length=50, null=True)
    apply_name = models.CharField('申请人', max_length=100, null=True)
    apply_time = models.DateField('申请时间', default=datetime.now)
    require_document = models.CharField('需求文档', max_length=100, null=True)
    upload_content = models.CharField('发布内容', max_length=200, null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据
    keyword = models.CharField('搜索关键字', max_length=100, null=True)
    program_status = models.CharField('项目发布状态', max_length=20, null=False, default='待审核')
    assembly_config = models.CharField('组件配置', max_length=100, null=True)
    branch = models.CharField('提测分支', max_length=100, null=True)
    tag = models.CharField('提测tag', max_length=50, null=True)
    raiseID = models.CharField('uat提测tag', max_length=50, null=True)
    raiseCommitID = models.CharField('uat提测commit ID', max_length=100, null=True)


class VersionUATManage(BaseTable):
    """
    SIT版本提测
    """

    class Mata:
        verbose_name = "UAT版本提测信息"
        db_table = "version_uat_manage"

    ENV = Choices(
        ('SIT', 'SIT'),
        ('UAT', 'UAT')
    )
    STATUESDATA = Choices(
        ('1', '待审核'),
        ('2', '审核通过，发布UAT'),
        ('3', '已发布UAT')
    )

    function_name = models.CharField('功能名称', max_length=100, db_index=True, null=True)
    project_name = models.CharField('工程名称', max_length=100, db_index=True, null=True)
    assembly_name = models.CharField('组件名称', max_length=100, db_index=True, null=True)
    service_list = models.CharField('服务列表', max_length=100, db_index=True, null=True)
    business_line = models.CharField('业务线', max_length=100, db_index=True, null=True)
    product_line = models.CharField('产品线', max_length=100, db_index=True, null=True)
    raise_test = models.CharField('提测sql脚本', max_length=50, db_index=True, null=True)
    sql_name = models.CharField('sql名称', max_length=100, db_index=True, null=True)
    sql_git_path = models.CharField('sql_git路径', max_length=100, db_index=True, null=True)
    raise_config_file = models.CharField('提测配置文件', max_length=50, db_index=True, null=True)
    service_name = models.CharField('服务名', max_length=100, db_index=True, null=True)
    public_config_path = models.CharField('公共配置', max_length=100, db_index=True, null=True)
    config_file_path = models.CharField('配置文件路径', max_length=100, db_index=True, null=True)
    test_man = models.CharField('测试维护人', max_length=50, db_index=True, null=True)
    develop_man = models.CharField('开发维护人', db_index=True, max_length=50, null=True)
    assemble_commit_id = models.CharField('组件提测commitID', max_length=100, null=True)
    product_version_now = models.CharField('版本号', max_length=50, null=True)
    apply_name = models.CharField('申请人', max_length=50, null=True)
    apply_time = models.DateField('申请时间', default=datetime.now)
    require_document = models.CharField('需求文档', max_length=100, null=True)
    upload_content = models.CharField('发布内容', max_length=200, null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据
    keyword = models.CharField('搜索关键字', max_length=50, null=True)
    program_status = models.CharField('项目发布状态', max_length=20, null=False, default='待审核')
    assembly_config = models.CharField('组件配置', max_length=100, null=True)
    branch = models.CharField('提测分支', max_length=100, null=True)
    tag = models.CharField('提测tag', max_length=50, null=True)
    raiseID = models.CharField('uat提测tag', max_length=50, null=True)
    raiseCommitID = models.CharField('uat提测commit ID', max_length=100, null=True)


class BusinessLineManage(BaseTable):
    """
    业务线
    """

    class Mata:
        verbose_name = "业务线"
        db_table = "businessline"

    business_line = models.CharField('业务线', max_length=50, db_index=True, null=True)


class ProductLineManage(BaseTable):
    """
    产品线
    """

    class Mata:
        verbose_name = "产品线"
        db_table = "productline"
    business_id = models.IntegerField(verbose_name='业务线ID', null=True)
    product_line = models.CharField('产品线', max_length=50, db_index=True, null=True)


class GitProData(BaseTable):
    """
    获取git项目总数保存入库
    """

    class Mata:
        verbose_name = '获取git项目总数保存入库'
        db_table = 'git_project'

    project_id = models.CharField("项目ID", max_length=50, db_index=True, null=True)
    project_name = models.CharField("项目名称", max_length=50, db_index=True, null=True)
    ssh_url_to_repo = models.CharField("SSH地址", max_length=150, db_index=True, null=True)
    http_url_to_repo = models.CharField("HTTP地址", max_length=150, db_index=True, null=True)


class GitProgrammeData(BaseTable):
    """
    根据工程名获取对应项目名
    """

    class Mata:
        verbose_name = '根据工程名获取对应项目名'
        db_table = 'git_programe'

    programme_id = models.CharField("工程ID", max_length=50, db_index=True, null=True)
    programme_name = models.CharField("工程名称", max_length=50, db_index=True, null=True)
    project_id = models.CharField("组件ID", max_length=50, db_index=True, null=True)
    project_name = models.CharField("组件名称", max_length=50, db_index=True, null=True)
    ssh_url_to_repo = models.CharField("SSH地址", max_length=150, db_index=True, null=True)
    http_url_to_repo = models.CharField("HTTP地址", max_length=150, db_index=True, null=True)


class RaiseOtherData(BaseTable):
    """
    获取其他提测内容
    """

    class Mata:
        verbose_name = '获取其他提测内容'
        db_table = 'raise_other_data'

    sql_files_name = models.CharField("sql文件名", max_length=50, db_index=True, null=True)
    sql_file_path = models.CharField("sql文件路径", max_length=50, db_index=True, null=True)
    data_clear_name = models.CharField("数据清洗文件名", max_length=50, db_index=True, null=True)
    data_clear_path = models.CharField("数据清洗文件路径", max_length=50, db_index=True, null=True)
    other_config_name = models.CharField("其他提测文件名", max_length=150, db_index=True, null=True)
    other_config_path = models.CharField("其他提测文件路径", max_length=150, db_index=True, null=True)
    assembly_name = models.CharField('组件名称', max_length=100, db_index=True, null=True)
    business_line = models.CharField('业务线', max_length=100, db_index=True, null=True)
    product_line = models.CharField('产品线', max_length=100, db_index=True, null=True)
    apply_time = models.DateField('申请时间', max_length=50, db_index=True, null=True)
    reportID = models.CharField('提测id', max_length=20, db_index=True, null=True)


class BaseRaiseInfo(BaseTable):
    """
    sit版本提测基础信息
    """

    class Mata:
        verbose_name = '版本提测基础信息'
        db_table = 'base_raise_info'

    system_name = models.CharField("提测系统名称", max_length=50, db_index=True,null=True)
    pro_name = models.CharField("项目名称", max_length=50, db_index=True,null=True)
    project_label = models.CharField("项目类型", max_length=50, db_index=True,null=True)
    raise_time = models.CharField("提测日期", max_length=50, db_index=True,null=True)
    raise_label = models.CharField("提测类型", max_length=50, db_index=True,null=True)
    raise_version = models.CharField("提测版本号", max_length=50, db_index=True,null=True)
    raise_people = models.CharField("提测人员", max_length=50, db_index=True,null=True)
    level = models.CharField("紧急程度", max_length=50, db_index=True,null=True)
    raise_env = models.CharField("提测环境", max_length=50, db_index=True,null=True)
    file_path = models.TextField("基线文档路径", default='', null=True)
    raise_content = models.TextField("提测内容",  default='', null=True)
    backstage_version = models.CharField("管理后台版本号", max_length=50, db_index=True,null=True)
    app_version = models.CharField("APP版本号", max_length=50, db_index=True,null=True)
    nose_version = models.CharField("前端版本号", max_length=50, db_index=True,null=True)
    develop_test_result = models.TextField("开发自测结果",  default='', null=True)
    focus_advise = models.TextField("测试关注重点与建议",  default='', null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据
    program_status = models.CharField('项目发布状态', max_length=20, null=False, default='待审核')
    checkContent = models.TextField("审核内容",  default='', null=True)
    checkResults = models.TextField("审核结果",  default='', null=True)
    raiseID = models.CharField("uat提测tag", max_length=50,db_index=True,null=True)
    raiseCommitID=models.CharField("uat提测commitID", max_length=100, db_index=True,null=True)


class SitConfigList(BaseTable):
    """
    配置列表
    """

    class Mata:
        verbose_name = '配置列表'
        db_table = 'sit_confg_list'

    assembly_name = models.CharField("组件名称", max_length=50, db_index=True, null=True)
    project_name = models.CharField("工程名称", max_length=50, db_index=True, null=True)
    config_info = models.CharField("配置信息", max_length=50, db_index=True, null=True)
    config_content = models.TextField("配置说明", default='', null=True)
    # ForeignKey为设置为外键，on_delete=models.CASCADE为级联关系，主表数据删除时，外键表的一同删除
    project = models.ForeignKey(BaseRaiseInfo, on_delete=models.CASCADE, db_constraint=False)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据


class SitOtherConfigData(BaseTable):
    """
    其他配置列表
    """

    class Mata:
        verbose_name = '其他配置列表'
        db_table = 'sit_other_config_data'

    other_label_select = models.CharField("类型选择", max_length=50, db_index=True, null=True)
    other_config_info = models.CharField("其他配置信息", max_length=50, db_index=True, null=True)
    other_config_filepath = models.CharField("其他配置文件路径", max_length=50, db_index=True, null=True)
    other_config_content = models.TextField("其他配置部署说明", default='', null=True)
    # ForeignKey为设置为外键，on_delete=models.CASCADE为级联关系，主表数据删除时，外键表的一同删除
    project = models.ForeignKey(BaseRaiseInfo, on_delete=models.CASCADE, db_constraint=False)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据


class sitFileList(BaseTable):
    """
    脚本列表
    """

    class Mata:
        verbose_name = '脚本列表'
        db_table = 'sit_file_list'

    script_name = models.CharField("脚本名称", max_length=50, db_index=True, null=True)
    script_git_path = models.CharField("GIT路径", max_length=50, db_index=True, null=True)
    script_label = models.CharField("脚本类型", max_length=50, db_index=True, null=True)
    script_content = models.TextField("部署说明",  default='', null=True)
    # ForeignKey为设置为外键，on_delete=models.CASCADE为级联关系，主表数据删除时，外键表的一同删除
    project = models.ForeignKey(BaseRaiseInfo, on_delete=models.CASCADE, db_constraint=False)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据



class sitOtherFileList(BaseTable):
    """
    其他脚本列表
    """

    class Mata:
        verbose_name = '其他脚本列表'
        db_table = 'sit_other_file_list'

    other_script_name = models.CharField("其他脚本名称", max_length=50, db_index=True, null=True)
    other_script_git_path = models.CharField("其他GIT路径", max_length=50, db_index=True, null=True)
    other_script_label = models.CharField("其他脚本类型", max_length=50, db_index=True, null=True)
    other_script_content = models.TextField("其他部署说明", default='', null=True)
    # ForeignKey为设置为外键，on_delete=models.CASCADE为级联关系，主表数据删除时，外键表的一同删除
    project = models.ForeignKey(BaseRaiseInfo, on_delete=models.CASCADE, db_constraint=False)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据


class sitAssemblyList(BaseTable):
    """
    组件提测列表
    """

    class Mata:
        verbose_name = '组件提测列表'
        db_table = 'sit_assembly_list'

    business_line = models.CharField("业务线", max_length=50, db_index=True,null=True)
    product_line = models.CharField("产品线", max_length=50, db_index=True,null=True)
    assembly_name = models.CharField("工程名称", max_length=50, db_index=True)
    project_name = models.CharField("组件名称", max_length=50, db_index=True)
    branch = models.CharField("提测分支", max_length=30, db_index=True, null=True)
    tag = models.CharField("提测tag", max_length=50, db_index=True, null=True)
    commitId = models.CharField("提测commitID", max_length=100, db_index=True,null=True)
    develop_man = models.CharField("开发负责人", max_length=50, db_index=True, null=True)
    test_man = models.CharField("测试负责人", max_length=50, db_index=True, null=True)
    product_version_now = models.CharField("生产版本号", max_length=50, db_index=True, null=True)
    uat_tag = models.CharField("UAT tag", max_length=100,db_index=True, null=True)
    uat_commitID = models.CharField("UAT commitID", max_length=150, db_index=True, null=True)
    # ForeignKey为设置为外键，on_delete=models.CASCADE为级联关系，主表数据删除时，外键表的一同删除
    project = models.ForeignKey(BaseRaiseInfo, on_delete=models.CASCADE, db_constraint=False)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据


class UatRaiseInfo(BaseTable):
    """
    uat版本提测基础信息
    """

    class Mata:
        verbose_name = 'uat版本提测基础信息'
        db_table = 'uat_raise_info'

    system_name = models.CharField("提测系统名称", max_length=50, db_index=True)
    pro_name = models.CharField("项目名称", max_length=50, db_index=True)
    project_label = models.CharField("项目类型", max_length=50, db_index=True)
    raise_time = models.CharField("提测日期", max_length=50, db_index=True)
    raise_label = models.CharField("提测类型", max_length=50, db_index=True)
    raise_people = models.CharField("提测人员", max_length=50, db_index=True)
    raise_version = models.CharField("提测版本号", max_length=50, db_index=True, null=True)
    level = models.CharField("紧急程度", max_length=50, db_index=True)
    raise_env = models.CharField("提测环境", max_length=50, db_index=True,null=True)
    file_path = models.TextField("基线文档路径",  default='', null=True)
    raise_content = models.TextField("提测内容",  default='', null=True)
    backstage_version = models.CharField("管理后台版本号", max_length=50, db_index=True, null=True)
    app_version = models.CharField("APP版本号", max_length=50, db_index=True, null=True)
    nose_version = models.CharField("前端版本号", max_length=50, db_index=True, null=True)
    develop_test_result = models.CharField("开发自测结果", max_length=50, db_index=True, null=True)
    focus_advise = models.CharField("测试关注重点与建议", max_length=255, db_index=True, null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据
    program_status = models.CharField('项目发布状态', max_length=20, null=False, default='待审核')
    # ForeignKey为设置为外键，on_delete=models.CASCADE为级联关系，主表数据删除时，外键表的一同删除
    project = models.ForeignKey(BaseRaiseInfo, on_delete=models.CASCADE, db_constraint=False)


class UatAssemblyList(BaseTable):
    """
    uat组件提测列表
    """

    class Mata:
        verbose_name = '组件提测列表'
        db_table = 'uat_assembly_list'

    business_line = models.CharField("业务线", max_length=50, db_index=True,null=True)
    product_line = models.CharField("产品线", max_length=50, db_index=True,null=True)
    assembly_name = models.CharField("工程名称", max_length=50, db_index=True)
    project_name = models.CharField("组件名称", max_length=50, db_index=True)
    branch = models.CharField("提测分支", max_length=30, db_index=True,null=True)
    tag = models.CharField("提测tag", max_length=50, db_index=True,null=True)
    commitId = models.CharField("提测commitID", max_length=100, db_index=True,null=True)
    develop_man = models.CharField("开发负责人", max_length=50, db_index=True, null=True)
    test_man = models.CharField("测试负责人", max_length=50, db_index=True, null=True)
    product_version_now = models.CharField("生产版本号", max_length=50, db_index=True, null=True)
    assembly_config = models.CharField("组件配置", max_length=50,db_index=True, null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据
    project = models.CharField("项目对应的id", max_length=10, db_index=True, null=True)
    system_name = models.CharField("提测系统名称", max_length=50, db_index=True,null=True)
    pro_name = models.CharField("项目名称", max_length=50, db_index=True,null=True)
    project_label = models.CharField("项目类型", max_length=50, db_index=True,null=True)
    raise_time = models.CharField("提测日期", max_length=50, db_index=True,null=True)
    raise_label = models.CharField("提测类型", max_length=50, db_index=True,null=True)
    raise_people = models.CharField("提测人员", max_length=50, db_index=True,null=True)
    level = models.CharField("紧急程度", max_length=50, db_index=True,null=True)
    raise_env = models.CharField("提测环境", max_length=50, db_index=True, null=True)
    program_status = models.CharField('项目发布状态', max_length=20, null=False, default='待审核')
    raiseID = models.CharField("uat提测tag", max_length=50,db_index=True,null=True)
    raiseCommitID=models.CharField("uat提测commitID", max_length=100, db_index=True,null=True)


class AccompanyTestList(BaseTable):
    """
    陪测产品列表
    """

    class Mata:
        verbose_name = '陪测产品列表'
        db_table = 'accompany_test_list'

    accompany_products = models.CharField("陪测产品", max_length=50, db_index=True,null=True)


class AccompanyListData(BaseTable):
    """
    陪测产品列表详细信息
    """

    class Mata:
        verbose_name = '陪测产品列表详细信息'
        db_table = 'accompany_list_data'

    AccompanyTestProducts = models.CharField("陪测产品", max_length=50, db_index=True, null=True)
    AccompanyTestVersion = models.CharField("陪测版本号", max_length=50, db_index=True, null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)  # 数据是否被删除。1代表显示数据
    # ForeignKey为设置为外键，on_delete=models.CASCADE为级联关系，主表数据删除时，外键表的一同删除
    project = models.ForeignKey(BaseRaiseInfo, on_delete=models.CASCADE, db_constraint=False)

