from django.urls import path
from quality_management.views import organization, code_defend
from quality_management.views import organization, version

urlpatterns = [
    # 组织架构文件
    path('organization_file/', organization.OrganizationApiView.as_view({
        "put": "upload_file",
        "get": 'list',
        "patch": "add",
    })),
    path('organization_file/<int:pk>/', organization.OrganizationApiView.as_view({
        "delete": "single_delete",
        "patch": "modify",
    })),
    # git commit提交数据
    path('git_commit/', code_defend.GitCommitApiView.as_view({
        "patch": "add_commit",
        "get": 'list_file',
    })),
    path('git_web_top_commit/', code_defend.GitCommitApiView.as_view({
        "get": 'web_top_list',
    })),
    path('git_web_bottom_commit/', code_defend.GitCommitApiView.as_view({
        "get": 'web_bottom_list',
    })),
    path('git_web_no_data_commit/', code_defend.GitCommitApiView.as_view({
        "get": 'web_no_data_list',
    })),
    path('git_api_top_commit/', code_defend.GitCommitApiView.as_view({
        "get": 'api_top_list',
    })),
    path('git_api_bottom_commit/', code_defend.GitCommitApiView.as_view({
        "get": 'api_bottom_list',
    })),
    path('git_api_no_data_commit/', code_defend.GitCommitApiView.as_view({
        "get": 'api_no_data_list',
    })),
    # 月版本
    path('month_version/', version.MonthVersionApiView.as_view({
        "get": 'list',
        "patch": "add",
    })),
    path('month_version/<int:pk>/', version.MonthVersionApiView.as_view({
        "delete": "single_delete",
        "patch": "modify",
    })),
    # 系统版本
    path('version/', version.VersionApiView.as_view({
        "get": 'list',
        "patch": "add",
        "delete": "multi_delete",
    })),
    path('version/<int:pk>/', version.VersionApiView.as_view({
        "delete": "single_delete",
        "patch": "modify",
    })),
    # 系统各版本
    path('child_version/', version.ChildVersionApiView.as_view({
        "get": 'list',
        "patch": "add",
        "delete": "multi_delete",
    })),
    path('child_version/<int:pk>/', version.ChildVersionApiView.as_view({
        "delete": "single_delete",
        "patch": "modify",
    })),
    # 所有版本信息
    path('all_version/', version.AllVersionApiView.as_view({
        "get": 'list',
    })),
]