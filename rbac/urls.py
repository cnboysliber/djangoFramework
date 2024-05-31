from django.urls import path, re_path
from django.conf.urls import url
from rbac.views import menu_list
urlpatterns = [
    # 服务列表
    path('rbac/', menu_list.ParentMenuProductsView.as_view({
        "get": "list",
    })),
]
