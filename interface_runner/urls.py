"""FasterRunner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import url
from interface_runner.views import \
    project, api, config, schedule, run, suite, report, yapi, test, websocket, db_config, fixture, ac_config, env

urlpatterns = [
    # 访问统计相关接口
    path('visit/', project.VisitView.as_view({
        "get": "list",
    })),

    # 项目相关接口地址
    path('project/', project.ProjectView.as_view({
        "get": "list",
        "post": "add",
        "patch": "update",
        "delete": "delete"
    })),
    path('project/<int:pk>/', project.ProjectView.as_view({"get": "single"})),

    # 定时任务相关接口
    path('schedule/', schedule.ScheduleView.as_view({
        "get": "list",
        "post": "add",
    })),

    path('schedule/<int:pk>/', schedule.ScheduleView.as_view({
        "get": "run",
        "delete": "delete",
        "put": "update"
    })),

    # debugtalk.py相关接口地址
    path('debugtalk/', project.DebugTalkView.as_view({
        "get": "list",
        "patch": "update",
        "post": "run"

    })),

    # 二叉树接口地址
    path('tree/<int:pk>/', project.TreeView.as_view({
        "get": "get",
        "patch": "patch",
        "post": "add"
    })),
    path('tree/', project.TreeView.as_view({
        "post": "add"
    })),

    # 导入yapi
    path('yapi/<int:pk>/', yapi.YAPIView.as_view()),

    # 文件上传 修改 删除接口地址
    # path('file/', project.FileView.as_view()),

    # api接口模板地址
    path('api/', api.APITemplateView.as_view({
        "post": "add",
        "get": "list"
    })),

    path('api/<int:pk>/', api.APITemplateView.as_view({
        "delete": "delete",
        "get": "single",
        "patch": "update",
        "post": "copy"
    })),

    path('api/tag/<int:pk>/', api.APITemplateView.as_view({
        "patch": "add_tag",  # api修改状态
    })),

    path('api/move_api/', api.APITemplateView.as_view({
        "patch": "move",  # api修改relation
    })),

    path('test/move_case/', suite.TestCaseView.as_view({
        "patch": "move",  # case修改relation
    })),

    path('api/sync/<int:pk>/', api.APITemplateView.as_view({
        "patch": "sync_case",  # api同步用例步骤
    })),

    # test接口地址
    path('test/', suite.TestCaseView.as_view({
        "get": "get",
        "post": "post",
        "delete": "delete"
    })),

    path('test/<int:pk>/', suite.TestCaseView.as_view({
        "delete": "delete",
        "post": "copy",
        "put": "put"  # 请求方法和处理方法同名时可以省略

    })),

    path('teststep/<int:pk>/', suite.CaseSuitInfoView.as_view({
        "get":"get",
    })),

    path('import_excel/', suite.CaseSuitInfoView.as_view({
        "put":"upload_excel",
    })),

    # config接口地址
    path('config/', config.ConfigView.as_view({
        "post": "add",
        "get": "list",
        "delete": "delete"
    })),

    path('config/<int:pk>/', config.ConfigView.as_view({
        "post": "copy",
        "delete": "delete",
        "patch": "update",
        "get": "all"
    })),

    # fixture地址
    path('fixtures/', fixture.FixtureViewSet.as_view({
        "post": "add",
        "get": "list",
        "delete": "delete",
        "patch": "update"
    })),
    path('fixtures/<int:pk>/', fixture.FixtureViewSet.as_view({
        "delete": "delete",
    })),

    path('variables/', config.VariablesView.as_view({
        "post": "add",
        "get": "list",
        "delete": "delete"
    })),

    path('variables/<int:pk>/', config.VariablesView.as_view({
        "delete": "delete",
        "patch": "update"
    })),

    # run api
    path('run_api_pk/<int:pk>/', run.run_api_pk),
    path('run_api_tree/', run.run_api_tree),
    path('run_api/', run.run_api),

    # run testsuite
    path('run_testsuite/', run.run_testsuite),
    path('run_test/', run.run_test),
    path('run_testsuite_pk/<int:pk>/', run.run_testsuite_pk),
    path('run_suite_tree/', run.run_suite_tree),

    path('run_testsuite_pk_websocket/<int:pk>/', run.run_testsuite_pk_websocket),

    # 报告地址
    path('reports/', report.ReportView.as_view({
        "get": "list"
    })),

    path('reports/<int:pk>/', report.ReportView.as_view({
        "delete": "delete",
        "get": "look"
    })),

    path('host_ip/', config.HostIPView.as_view({
        "post": "add",
        "get": "list"
    })),

    path('host_ip/<int:pk>/', config.HostIPView.as_view({
        "delete": "delete",
        "patch": "update",
        "get": "all"
    })),
    url('run/', test.RunCaseView.as_view({
        "post": "add",
    })),

    # 数据库配置
    path('db_config/<int:pk>/', db_config.DBConfigView.as_view({
        'delete': 'delete',
        'patch': 'update',
    })),
    path('db_config/', db_config.DBConfigView.as_view({
        'get': 'list',
        'post': 'add',
        'delete': 'delete',
        'patch': 'update',
    })),

    path('ac_config/<int:pk>/', ac_config.AccountConfigView.as_view({
        'delete': 'delete',
        'patch': 'update',
    })),
    path('ac_config/', ac_config.AccountConfigView.as_view({
        'get': 'list',
        'post': 'add',
    })),
    path('env/', env.EnvView.as_view({
        'get': 'list',
    })),

    # websocket api
    url('test_login/', websocket.test_web),
    url('web/', websocket.get_run_case_log),
    url('webs/', websocket.get_output_su),
]
