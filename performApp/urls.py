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
from django.conf import settings
from django.urls import path, re_path
from django.conf.urls import url
from django.views.static import serve

from performApp.views import performReport, \
    coverage, testType,  performProject, servicesServer, bugs
from performApp.views import performServer, performScenes, performScript, \
    performEnv

urlpatterns = [
    # 性能报告
    path('perform_report/', performReport.PerformReportView.as_view({
        "get": "list",
        "put": "upload_excel",
        "patch": "add",
        "delete": "multi_delete",
        'post': "report_exist"
    })),
    path('perform_report/<int:pk>/', performReport.PerformReportView.as_view({
        "delete": "single_delete",
        "patch": "modify",
        "put": "upload_jtl",
        'get': "get_detail",
    })),

    # 测试类型
    path('test_type/', testType.TestTypeView.as_view({
        "get": "query",
        "patch": "add",
        "delete": "multi_delete"
    })),
    path('test_type/<int:pk>/', testType.TestTypeView.as_view({
        "delete": "single_delete",
        "patch": "modify",
        'get': "get_detail"
    })),

    # 代码覆盖率
    path('services/<int:pk>/', coverage.CoverageServiceView.as_view({
        "delete": "single_delete",
        "patch": "modify",
        'get': "get_detail"
    })),
    path('services/', coverage.CoverageServiceView.as_view({
        "get": "list",
        "patch": "add",
        "delete": "multi_delete"
    })),
    path('coverageTask/', coverage.CoverageTaskView.as_view({
        "post": "run_single",
        'get': "log",
        'patch': 'batch_run'
    })),
    # 代码覆盖率日志
    path('coverageLog/', coverage.CoverageTaskView.as_view({
        'get': "view_log",
    })),

    # 性能项目管理
    path('project/', performProject.PerformProjectView.as_view({
        'get': 'list',
        'patch': 'add',
        'delete':  'multi_delete'
    })),
    path('project/<int:pk>/', performProject.PerformProjectView.as_view({
        'get': 'get_detail',
        'patch': 'modify',
        'delete':  'single_delete'
    })),

    # 压力机管理
    path('perform_server/', performServer.PerformServerView.as_view({
        "get": "query",
        "patch": "add",
        "delete": "multi_delete"
    })),
    path('perform_server/<int:pk>/', performServer.PerformServerView.as_view({
        "delete": "single_delete",
        "patch": "modify",
        'get': "get_detail"
    })),
    path('perform_work/', performServer.JmeterWorkView.as_view({
        'get': 'get_work_list',
        'post': 'action_worker'
    })),
    # 性能环境管理
    path('perform_env/', performEnv.PerformEnvView.as_view({
        'get': 'list',
        'patch': 'add',
        'delete':  'multi_delete'
    })),
    path('perform_env/<int:pk>/', performEnv.PerformEnvView.as_view({
        'get': 'get_detail',
        'patch': 'modify',
        'delete':  'single_delete'
    })),
    # 性能服务的地址管理
    path('service_server/', servicesServer.ServicesServerView.as_view({
        'get': 'list',
        'patch': 'add',
        'delete':  'multi_delete'
    })),
    path('service_server/<int:pk>/', servicesServer.ServicesServerView.as_view({
        'get': 'get_detail',
        'patch': 'modify',
        'delete':  'single_delete'
    })),

    # 场景管理
    path('scenes_manage/', performScenes.PerformScenesView.as_view({
        "get": "list",
        "patch": "add",
        "delete": "multi_delete",
        "post": "get_transaction_data",
    })),
    path('scenes_task/', performScenes.PerformScenesView.as_view({
        'post': 'run_task',
        'patch': 'stop_task',
        'get': 'get_task_list',
        'put': 'remark_task'
    })),
    path('scenes_report/', performScenes.PerformScenesView.as_view({
        'get': 'get_tps_chart_data',
        'post': 'get_scene_transactions'
    })),
    path('scenes_manage/<int:pk>/', performScenes.PerformScenesView.as_view({
        "delete": "single_delete",
        "patch": "modify",
        'get': "get_detail",
    })),
    path('scenes_config/<int:pk>/', performScenes.PerformScenesView.as_view({
        "post": "add_jconfig",
        'get': "get_jconfig",
        "patch": "patch_jconfig",
    })),
    # 性能结果
    path('perform_result/', performScenes.PerformScenesView.as_view({
        'get': 'get_perform_result'
    })),

    # 场景定时任务
    path('scenes_schedule/', performScenes.PerformScenesPlanView.as_view({
        "post": "patch_schedule_scene",
        "put": "stop_schedule_scene"
    })),

    path('error_log_download/', performScenes.PerformScenesView.as_view({
        "get": "download_error_log"
    })),

    # 脚本管理
    path('script_manage/', performScript.PerformScriptView.as_view({
        "get": "list",
        "patch": "add",
        "delete": "multi_delete",
        "post": "single_delete",

    })),
    path('script_download/', performScript.PerformScriptView.as_view({
        "get": "down_script",
    })),
    path('script_manage/<int:pk>/', performScript.PerformScriptView.as_view({
        "delete": "single_delete",
        "patch": "modify",
        'get': "get_detail"
    })),
    # 压测参数化文件
    path('script_params/', performScript.PerformScriptParamsView.as_view({
        "post": "list",
        "get": "download"
    })),

    # Bugs管理
    path('bugs/', bugs.BugsView.as_view({
        "get": "list",
        "post": "add",
        "delete": "multi_delete",
    })),
    path('bugs/<int:pk>/', bugs.BugsView.as_view({
        "delete": "single_delete",
        "post": "modify",
        'get': "get_detail",
    })),
    path('down_bug/', bugs.BugsView.as_view({
        "get": "down_bug"
    })),

    # 场景copy
    path('copy_scenes/', performScenes.PerformScenesView.as_view({
        "post": "copy_scenes",
    })),
]
