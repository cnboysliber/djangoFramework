# -*- coding: utf-8
import uuid
from datetime import datetime

from django.db import models
from model_utils import Choices
from FasterRunner import const as cnt


class BaseTable(models.Model):
    """
    公共字段列
    """

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        app_label = 'performApp'

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    creator = models.CharField(verbose_name="创建人", max_length=20, null=True)
    updater = models.CharField(verbose_name="更新人", max_length=20, null=True)


class PerformReport(models.Model):

    class Meta:
        db_table = 'performReport'
        app_label = 'performApp'

    ITEMS = Choices(
        (1, 'B端'),
        (2, 'C端'),
        (3, '小程序'),
        (4, 'pc'),
        (5, 'H5'),
        (6, 'SAAS'),
        (7, 'H5_mbrand'),
        (8, '车盟宝小程序'),
        (20, '其他'),
    )
    ENVS = Choices(
        (1, 'uat'),
        (2, 'uat2'),
        (3, 'pro')
    )
    TYPES = Choices(
        (1, '单压'),
        (2, '混压'),
    )

    api_env = models.IntegerField(verbose_name='接口环境', choices=ENVS, default=1, db_index=True, null=True)
    api_name = models.CharField(max_length=100, verbose_name='接口名称', db_index=True, null=True)
    api_url = models.CharField(max_length=500, verbose_name='接口url', default='', null=True)
    api_index = models.IntegerField(verbose_name='接口编号', default=1, null=True, blank=True)
    module = models.CharField(max_length=64, verbose_name='模块名称', db_index=True, null=True)
    component = models.CharField(max_length=255, verbose_name='组件名称', db_index=True, null=True)
    manage_name = models.CharField(max_length=64, verbose_name='交易名称', default='', null=True)
    sys_version = models.CharField(max_length=60, verbose_name='系统版本号', default='', null=True)
    api_version = models.CharField(max_length=60, verbose_name='接口版本号', db_index=True, null=True)
    ptype = models.SmallIntegerField(verbose_name='压测类型', choices=TYPES, db_index=True, null=True, default=1)
    item = models.SmallIntegerField(verbose_name='端', choices=ITEMS, db_index=True, null=True)
    req_count = models.IntegerField(verbose_name='并发请求数', null=True)
    resp_ms_90 = models.IntegerField(verbose_name='90%响应时间(ms)', null=True)
    resp_ms_99 = models.IntegerField(verbose_name='99%响应时间(ms)', null=True)
    err_rate = models.IntegerField(verbose_name='错误率 * 100', blank=True, null=True)
    tps = models.IntegerField(verbose_name='TPS * 10', null=True)
    req_time = models.DateField(verbose_name='压测日期', default=datetime.now)
    req_period = models.CharField(max_length=32, verbose_name='压测时间段')
    result = models.TextField(verbose_name='压测结果', default='', blank=True, null=True)
    status = models.SmallIntegerField(verbose_name='状态', default=1)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)


class PerformProject(BaseTable):
    """
    性能测试项目管理
    """
    class Meta:
        db_table = 'performManage'

    TYPES = Choices(
        (1, '一般'),
        (2, '回归'),
    )
    RUN_STATUS = Choices(
        (0, '待执行'),
        (1, '执行中'),
        (2, '执行完成'),
    )

    project = models.CharField(max_length=100, verbose_name='项目名称', db_index=True)
    desc = models.CharField(max_length=500, verbose_name='项目描述', default='')
    ptype = models.SmallIntegerField(verbose_name='项目类型', choices=TYPES, default=1)
    # version = models.CharField(max_length=30, verbose_name='项目版本号')
    dev_manager = models.CharField(max_length=60, verbose_name='开发负责人', db_index=True)
    developer = models.CharField(max_length=60, verbose_name='开发人员')
    tester = models.CharField(max_length=60, verbose_name='测试人员')
    run_status = models.SmallIntegerField(verbose_name='执行状态', choices=RUN_STATUS, default=0)
    err_rate = models.IntegerField(verbose_name='错误率，以整数记录', default=0, null=True)
    demand_start = models.CharField(max_length=30, verbose_name='需求梳理开始时间', null=True, blank=True)
    demand_end = models.CharField(max_length=30, verbose_name='需求梳理结束时间', null=True)
    api_start = models.CharField(max_length=30, verbose_name='接口梳理开始时间', null=True)
    api_end = models.CharField(max_length=30, verbose_name='接口梳理结束时间', null=True)
    script_start = models.CharField(max_length=30, verbose_name='脚本调试开始时间', null=True)
    script_end = models.CharField(max_length=30, verbose_name='脚本调试结束时间', null=True)
    data_start = models.CharField(max_length=30, verbose_name='造数开始时间', null=True)
    data_end = models.CharField(max_length=30, verbose_name='造数结束时间', null=True)
    run_start = models.CharField(max_length=30, verbose_name='测试开始时间', null=True)
    run_end = models.CharField(max_length=30, verbose_name='测试结束时间', null=True)
    completed = models.CharField(max_length=30, verbose_name='测试计划完成时间', null=True)
    status = models.SmallIntegerField(verbose_name='删除状态，0表示删除', default=1)


class TestType(BaseTable):
    """
    性能测试类型
    """
    class Meta:
        db_table = 'testType'

    name = models.CharField(max_length=60, verbose_name='测试类型', null=False)
    status = models.SmallIntegerField(verbose_name='删除状态，0表示删除', default=1)


class ScenesManage(BaseTable):
    """
    性能测试场景管理
    """
    class Meta:
        db_table = 'scenes'

    TYPES = Choices(
        (1, '单场景'),
        (2, '混合场景'),
    )
    STATES = Choices(
        (1, '待运行'),
        (2, '运行中'),
        (3, '成功'),
        (4, '失败'),
    )
    ITEMS = Choices(
        (1, 'B端'),
        (2, 'C端'),
        (3, '其他'),
    )
    SCHEDULER = Choices(
        (0, '未定时'),
        (1, '周期运行'),
        (2, '定时运行'),
    )
    version = models.CharField(max_length=30, verbose_name='项目版本号', default='')
    scene_uid = models.CharField(max_length=64, null=True, verbose_name='场景的uid')
    project_id = models.IntegerField(verbose_name='性能项目ID', null=False, db_index=True)
    scene_name = models.CharField(max_length=60, verbose_name='场景名称', null=False)
    remark = models.CharField(max_length=300, verbose_name='场景描述/备注', default='')
    item = models.SmallIntegerField(verbose_name='测试端', choices=ITEMS, null=False, default='')
    sType = models.SmallIntegerField(verbose_name='场景类型', choices=TYPES, null=False, default='')
    test_type = models.IntegerField(verbose_name='测试方法,多个以逗号分隔', null=True,)
    script_id = models.IntegerField(verbose_name='测试脚本ID', null=True, blank=True)
    client_num = models.IntegerField(verbose_name='测试压力服务器个数', null=False, default=1)
    state = models.SmallIntegerField(verbose_name='运行状态', choices=STATES, null=False, default=1)
    status = models.SmallIntegerField(verbose_name='删除状态，0表示删除', default=1)


class PerformSceneRelation(models.Model):
    """
    压测任务对应的关系表
    """
    class Meta:
        db_table = 'PerformSceneRelation'
        app_label = 'performApp'

    uid = models.CharField(max_length=60, default=uuid.uuid4, verbose_name='运行的UUID')
    scene_id = models.IntegerField(verbose_name='场景ID')
    server_id = models.IntegerField(verbose_name='服务器对应的ID')
    status = models.SmallIntegerField(verbose_name='是否有效状态，0表示无效', default=1)


class PerformEnv(BaseTable):
    """
    压测环境
    """

    ENV_TYPES = Choices(
        (1, 'sit'),
        (2, 'uat'),
        (3, 'uat2'),
        (4, 'dev'),
        (5, 'prod')
    )

    class Meta:
        db_table = 'PerformEnvManage'

    name = models.CharField(max_length=100, verbose_name='环境名称')
    desc = models.CharField(max_length=300, verbose_name='环境描述', null=True)
    project_id = models.IntegerField(verbose_name='项目ID', null=False, default=0)
    env_type = models.SmallIntegerField(verbose_name='环境类型', choices=ENV_TYPES)
    status = models.SmallIntegerField(verbose_name='删除状态', default=1)


class ServicesServer(BaseTable):
    """
    服务管理信息
    """
    class Meta:
        db_table = 'ServicesServer'

    ENV_TYPES = Choices(
        (1, 'sit'),
        (2, 'uat'),
        (3, 'uat2'),
        (4, 'dev'),
        (5, 'prod')
    )
    SERVER_TYPES = Choices(
        (1, 'DB'),
        (2, '应用'),
        (3, 'Nginx'),
        (4, '网关'),
        (5, 'redis')
    )
    OS_TYPES = Choices(
        (1, 'Linux'),
        (2, 'Windows'),
        (3, 'IOS')
    )

    env_id = models.IntegerField(verbose_name='环境管理ID', null=False)
    server_type = models.SmallIntegerField(verbose_name='服务类型', choices=SERVER_TYPES)
    server_ip = models.CharField(max_length=40, verbose_name='ip地址')
    cpus = models.IntegerField(verbose_name='服务器CPU', null=False)
    memory = models.IntegerField(verbose_name='内存GB', null=False)
    os_type = models.SmallIntegerField(verbose_name='系统类型', null=False, choices=OS_TYPES)
    status = models.SmallIntegerField(verbose_name='删除状态，0表示删除', default=1)


class PerformScript(BaseTable):
    """
    jmt脚本
    """
    class Meta:
        db_table = 'performScript'

    FILE_TYPE = Choices(
        (0, '脚本文件'),
        (1, '参数文件'),
    )

    scene_uid = models.CharField(max_length=64, verbose_name='场景uid', null=True)
    file_type = models.SmallIntegerField(verbose_name='文件类型', choices=FILE_TYPE, default=0)
    name = models.CharField(max_length=100, verbose_name='文件名称', default='')
    desc = models.CharField(max_length=300, verbose_name='文件备注', default='')
    data = models.TextField(verbose_name='脚本详情', default='', null=True)
    state = models.SmallIntegerField(verbose_name='运行状态', default=1)
    status = models.SmallIntegerField(verbose_name='删除状态，0表示删除', default=1)


class PerformScriptParams(models.Model):
    """
    脚本的参数化文件
    """
    class Meta:
        db_table = 'PerformScriptParams'
        app_label = 'performApp'

    uid = models.CharField(max_length=64, verbose_name='脚本对应UUID值', default='')
    script_id = models.IntegerField(verbose_name='脚本对应对的ID', null=False)
    name = models.CharField(max_length=100, verbose_name='脚本名称', null=False)
    status = models.SmallIntegerField(verbose_name='删除状态，0表示删除', default=1)


class Bugs(BaseTable):
    """
    性能压测缺陷
    """
    class Meta:
        db_table = 'bugs'

    BUGSSTATE = Choices(
        (1, '打开'),
        (2, '处理中'),
        (3, '完成'),
        (4, '关闭'),
    )

    SEVERITIES = Choices(
        (1, '致命'),
        (2, '严重'),
        (3, '一般'),
        (4, '提示'),
        (5, '建议'),
    )

    project_id = models.IntegerField(verbose_name='关联的项目ID', null=False)
    tapd_bug_id = models.CharField(max_length=20, verbose_name='tapd对应的缺陷ID')
    bug_severity = models.SmallIntegerField(verbose_name='缺陷严重程度', choices=SEVERITIES)
    scene_id = models.IntegerField(verbose_name='场景ID')
    api_name = models.CharField(max_length=100, verbose_name='接口名称')
    api_url = models.CharField(max_length=200, verbose_name='接口URL')
    describe = models.CharField(max_length=500, verbose_name='缺陷描述', default='')
    developer = models.CharField(max_length=60, verbose_name='开发人员')
    manager = models.CharField(max_length=60, verbose_name='开发负责人')
    state = models.SmallIntegerField(verbose_name='缺陷状态', choices=BUGSSTATE, default=1)
    field_img_one = models.CharField(max_length=500, verbose_name='缺陷图片，多张图片以,号分开', default='')
    comment = models.CharField(max_length=500, verbose_name='修复后情况描述', default='')
    field_img_two = models.CharField(max_length=500, verbose_name='修复后图片，多张图片以,号分开', default='')
    status = models.SmallIntegerField(verbose_name='删除状态，0表示删除', default=1)


class PerformServer(BaseTable):
    """
    压力机服务器管理
    """

    Types = Choices(
        (0, 'slave'),
        (1, 'master'),
    )

    class Meta:
        db_table = 'PerformServer'

    # scene_id = models.IntegerField(verbose_name='占用的场景ID', null=True, blank=True)
    name = models.CharField(max_length=60, verbose_name='服务器名称')
    desc = models.CharField(max_length=200, verbose_name='服务器描述', default='')
    srv_type = models.SmallIntegerField(verbose_name='服务器类型，slave/master', choices=Types, default=0)
    server_ip = models.CharField(max_length=40, verbose_name='服务器IP')
    cpus = models.SmallIntegerField(verbose_name='CPU')
    memory = models.SmallIntegerField(verbose_name='内存')
    weight = models.IntegerField(verbose_name='服务器权重, 最大值100，最小0', default=100)
    used = models.SmallIntegerField(verbose_name='是否空闲，1表示空闲', default=cnt.ACTIVE)
    status = models.SmallIntegerField(verbose_name='删除状态，0表示删除', default=1)


class ApiPerformancePlan(BaseTable):
    """
    接口压测执行计划
    """
    class Meta:
        db_table = 'ApiPerformancePlan'

    STATES = Choices(
        (0, '暂停'),
        (1, '启动')
    )
    TYPES = Choices(
        (1, '周期'),
        (2, '定时')
    )

    scene_id = models.IntegerField(verbose_name='关联场景ID', null=False)
    plan_type = models.SmallIntegerField(verbose_name='场景定时类型，周期、定时任务两种类型', choices=TYPES, null=True)
    plan_time = models.CharField(max_length=100, verbose_name='定时执行时间', null=True)
    module = models.CharField(max_length=200, verbose_name='定时任务task方法，如module.func', null=True)
    state = models.SmallIntegerField(verbose_name='定时状态', default=1, choices=STATES)
    status = models.SmallIntegerField(verbose_name='数据是否删除', default=1)


class JacocoService(models.Model):
    """
    代码覆盖率测试
    """

    TYPES = Choices(
        (0, 'docker'),
        (1, 'tomcat')
    )

    class Meta:
        db_table = 'JacocoService'
        app_label = 'performApp'

    service_name = models.CharField(max_length=60, null=False)
    module = models.CharField(max_length=60, verbose_name='服务所属模块名')
    git_path = models.CharField(max_length=200, verbose_name='git上的源码路径', null=True)
    sonar_project_key = models.CharField(max_length=200, verbose_name='sonar服务key', null=True)
    nacos_name = models.CharField(max_length=50, verbose_name='服务在nacos名称', null=True)
    jenkins_job = models.CharField(max_length=60, verbose_name='jenkins上的job名称', null=True)
    # jacoco_port_type = models.SmallIntegerField(verbose_name='jacoco端口号类型', default='2')
    server_ip = models.CharField(max_length=60, verbose_name='部署服务器IP', null=True)
    service_path = models.CharField(max_length=255, verbose_name='服务器上部署的包全路径', null=True)
    dtype = models.SmallIntegerField(verbose_name='部署类型，0：docker，1: tomcat', default=0, choices=TYPES)
    service_port = models.IntegerField(verbose_name='服务部署端口号', default=0, null=True)

    status = models.SmallIntegerField(verbose_name='状态', default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class JacocoTask(models.Model):
    """
    Jacoco任务
    """
    class Meta:
        db_table = 'JacocoTask'
        app_label = 'performApp'

    STATES = Choices(
        (0, '待运行'),
        (1, '运行中'),
        (2, '成功'),
        (3, '失败'),
    )

    uid = models.CharField(max_length=60, default=uuid.uuid4, verbose_name='运行的UUID')
    service_id = models.CharField(max_length=60, verbose_name='对应的服务ID', null=False)
    state = models.SmallIntegerField(verbose_name='任务运行状态', choices=STATES)
    log = models.TextField(verbose_name='任务运行状态', default='')

    status = models.SmallIntegerField(verbose_name='状态', default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class PerformJmeterData(models.Model):
    """
    压测接口结果
    """

    class Meta:
        db_table = 'performJmeterResult'
        app_label = 'performApp'

    scene_id = models.CharField(max_length=60, default='', verbose_name='场景id')
    task_id = models.CharField(max_length=32, verbose_name='压测运行任务ID')
    transaction = models.CharField(max_length=300, verbose_name='压测接口名')
    avg = models.IntegerField(verbose_name='压测的平均响应时间*100', default=0)
    pct90 = models.IntegerField(verbose_name='压测的pct90时间*100', default=0)
    pct95 = models.IntegerField(verbose_name='压测的pct95时间*100', default=0)
    pct99 = models.IntegerField(verbose_name='压测的pct99时间*100', default=0)
    req_count = models.IntegerField(verbose_name='压测总请求个数', default=0)
    req_err_count = models.IntegerField(verbose_name='压测错误响应数', default=0)
    tps = models.IntegerField(verbose_name='压测接口平均tps', default=0)
    flag = models.IntegerField(verbose_name='报告标记，0表示普通报告，1表示正式报告', default=0)
    create_time = models.DateTimeField(auto_now_add=True)


class PerformResultView(models.Model):
    """
    压测任务正式报告的视图
    """

    class Meta:
        managed = False
        db_table = 'remarkTaskResult'
        app_label = 'performApp'

    id = models.IntegerField('ID', primary_key=True)
    project = models.CharField(max_length=200, null=True, verbose_name='压测项目名称')
    project_id = models.IntegerField(null=True, verbose_name='压测项目Id')
    scene_name = models.CharField(max_length=200, verbose_name='场景名称', null=True)
    version = models.CharField(max_length=60, verbose_name='场景版本', null=True)
    task_id = models.CharField(max_length=32, verbose_name='压测运行任务ID')
    transaction = models.CharField(max_length=300, verbose_name='压测接口名')
    pct90 = models.IntegerField(verbose_name='压测的pct90时间*100', default=0)
    pct95 = models.IntegerField(verbose_name='压测的pct95时间*100', default=0)
    pct99 = models.IntegerField(verbose_name='压测的pct99时间*100', default=0)
    req_count = models.IntegerField(verbose_name='压测总请求个数', default=0)
    req_err_count = models.IntegerField(verbose_name='压测错误响应数', default=0)
    tps = models.IntegerField(verbose_name='压测接口平均tps', default=0)









