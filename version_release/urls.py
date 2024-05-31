from django.urls import path, re_path
from django.conf.urls import url
from version_release.views import service_list,version_test,version_uat_test,buss_line,pro_line,git_projects,raise_other,sit_base_info,sit_other_config_list,sit_config_list,sit_file_list,sit_other_file_list,sit_raise_info,sit_baseInfo_detail,uat_raise_info,uat_assembly_info,accompamy_products,accompany_list_info

urlpatterns = [
    # 服务列表
    path('version_release/', service_list.PerformView.as_view({
        "get": "list",
        "patch": "add",
        "delete": "multi_delete"
    })),
    path('version_release/<int:pk>/', service_list.PerformView.as_view({
        "delete": "single_delete",
        'get': "get_detail",
        "patch": "modify",
    })),
    path('version_releases/<str:pk>/', service_list.PerformView.as_view({
        'get': "get_service_detail"
    })),
    #获取业务线列表
    path('version_business_list/', service_list.PerformView.as_view({
            'get': "business_list"
        })),
    # 获取产品线列表
    path('version_product_list/', service_list.PerformView.as_view({
        'get': "product_list"
    })),
    path('getProAssembly/', service_list.PerformView.as_view({
        "get": "get_proAssembly_name",
    })),
    #选择产品业务线后获取组件与工程名
    path('getProAssemblyLine/', service_list.PerformView.as_view({
        "get": "get_proAssembly__line",
    })),
    # 获取功能名称列表
    path('version_function_list/', service_list.PerformView.as_view({
        'get': "function_list"
    })),
    # 获取工程名称列表
    path('version_project_list/', service_list.PerformView.as_view({
        'get': "project_list"
    })),
    # 获取组件名称列表
    path('version_assembly_list/', service_list.PerformView.as_view({
        'get': "assembly_list"
    })),
    #获取开发维护人列表
    path('version_develop_list/', service_list.PerformView.as_view({
        'get': "develop_list"
    })),
    # 获取测试维护人列表
    path('version_test_list/', service_list.PerformView.as_view({
        'get': "test_list"
    })),
    # 获取测试维护人列表
    path('get_project_data/', service_list.PerformView.as_view({
        'get': "get_project_data"
    })),


    #SIT版本提测
    path('version_test/', version_test.VersionTestView.as_view({
        "get": "list",
        "patch": "add",
        "delete": "multi_delete"
    })),
    path('version_test/<int:pk>/', version_test.VersionTestView.as_view({
        "delete": "single_delete",
        'get': "get_detail",
        "patch": "modify",
    })),

    # UAT版本提测
    path('version_uat_test/', version_uat_test.VersionUATView.as_view({
        "get": "list",
        "post": "upload_excel",
        "patch": "add",
        "delete": "multi_delete"
    })),
    path('version_uat_test/<int:pk>/', version_uat_test.VersionUATView.as_view({
        "delete": "single_delete",
        "patch": "modify",
        'get': "get_detail"
    })),
    # 首页柱状图图表信息
    path('data_list/', version_test.VersionTestView.as_view({
        "get": "data_list",
    })),
    # 首页柱状图图表信息
    path('program_status_list/', version_test.VersionTestView.as_view({
        "get": "program_status_list",
    })),
    # # 获取业务线
    # path('busi_line/', buss_line.BussnessView.as_view({
    #     "get": "list",
    # })),
    # # 获取产品线
    # path('pro_line/', pro_line.ProductView.as_view({
    #     "get": "list",
    # })),
    #获取git项目数据
    path('git_message/', git_projects.GitProjectsView.as_view({
        "get": "list",
    })),
    path('get_projectId/', git_projects.GitProjectsView.as_view({
        "get": "get_detail",
    })),
    path('get_service_projectId/', git_projects.GitProjectsView.as_view({
        "get": "get_sevice_detail",
    })),
    path('getbranches/<pk>/', git_projects.GitProjectsView.as_view({
        "get": "get_branches",
    })),
    path('get_tag/<pk>/', git_projects.GitProjectsView.as_view({
        "get": "get_tag",
    })),
    path('getProjectName/', git_projects.GitProjectsView.as_view({
        "get": "get_project_name",
    })),

    path('getProjectList/', git_projects.GitProjectsView.as_view({
        "get": "get_project_list",
    })),
    ##获取所有的工程名称
    path('getProgrammeList/', git_projects.GitProjectsView.as_view({
        "get": "get_programe_list",
    })),
    ##获取对应分支的commits
    path('getCommits/<pk>/', git_projects.GitProjectsView.as_view({
        "get": "get_commitID",
    })),
    # 其他提测
    path('raise_other/', raise_other.RaiseOtherView.as_view({
        "patch": "add",
    })),
    path('raise_other_data/', raise_other.RaiseOtherView.as_view({
        "get": "get_detail",
    })),
    ##sit 基础提测信息提测
    path('sit_base_info/', sit_base_info.BaseRaiseInfoView.as_view({
        "get": "list",
        "patch": "add",
    })),
    path('sit_base_info/<str:pk>/', sit_base_info.BaseRaiseInfoView.as_view({
        "get": "get_detail",
        "patch": "modify",
        "delete": "single_delete",
    })),
    ##sit 审核通过接口
    path('sit_base_check/<str:pk>/', sit_base_info.BaseRaiseInfoView.as_view({
        "patch": "CheckModify",
    })),
    ##uat提测tag commitID
    path('sit_base_tag_commit/<str:pk>/', sit_base_info.BaseRaiseInfoView.as_view({
        "patch": "RaiseModify",
    })),
    ##sit 配置信息提测
    path('config_list/', sit_config_list.ConfigListView.as_view({
        "patch": "add",
    })),
    path('config_list/<str:pk>/', sit_config_list.ConfigListView.as_view({
        "get": "get_detail",
        "patch": "modify",
    })),
    ##sit 其他配置信息提测
    path('other_config_list/', sit_other_config_list.OtherConfigListView.as_view({
        "patch": "add",
    })),
    path('other_config_list/<str:pk>/', sit_other_config_list.OtherConfigListView.as_view({
        "get": "get_detail",
        "patch": "modify",
    })),
    ##sit脚本列表提测
    path('file_list/', sit_file_list.fileListView.as_view({
        "patch": "add",
    })),
    path('file_list/<str:pk>/', sit_file_list.fileListView.as_view({
        "get": "get_detail",
        "patch": "modify",
    })),
    ##sit 其他脚本列表提测
    path('other_file_list/', sit_other_file_list.OtherFileListView.as_view({
        "patch": "add",
    })),
    path('other_file_list/<str:pk>/', sit_other_file_list.OtherFileListView.as_view({
        "get": "get_detail",
        "patch": "modify",
    })),
    ##sit提测接口
    # SIT版本提测
    path('sit_raise_info/', sit_raise_info.SitRaiseInfoView.as_view({
        "get": "list",
        "patch": "add",
        "delete": "multi_delete"
    })),
    path('sit_raise_info/<int:pk>/', sit_raise_info.SitRaiseInfoView.as_view({
        "delete": "single_delete",
        'get': "get_detail",
        "patch": "modify",
    })),
    ##sit提测删除功能
    path('sit_del_info/<int:pk>/', sit_baseInfo_detail.DelInfoView.as_view({
        "delete": "single_delete",
    })),
    ##UAT 提测基本信息
    path('uat_base_info/', uat_raise_info.UatRaiseInfoView.as_view({
        "get": "list",
        "patch": "add",
    })),
    path('uat_base_info/<str:pk>/', uat_raise_info.UatRaiseInfoView.as_view({
        "get": "get_detail",
        "patch": "modify",
        "delete": "single_delete",
    })),
    # SIT版本提测
    path('uat_raise_info/', uat_assembly_info.UatAssemblyInfoView.as_view({
        "get": "list",
        "patch": "add",
        "delete": "multi_delete"
    })),
    path('uat_raise_info/<int:pk>/', uat_assembly_info.UatAssemblyInfoView.as_view({
        "delete": "single_delete",
        'get': "get_detail",
        "patch": "modify",
    })),
    ##陪测产品列表
    path('accompany_products/', accompamy_products.AccompanyProductsView.as_view({
        "get": "list",
    })),
    ##陪测产品详细信息
    path('accompany_list/', accompany_list_info.AccompanyListInfoView.as_view({
        "patch": "add",
    })),
    path('accompany_list/<str:pk>/', accompany_list_info.AccompanyListInfoView.as_view({
        "get": "get_detail",
        "patch": "modify",
    })),
]
