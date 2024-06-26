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

from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url
from fastuser import views
from interface_runner.views import timer_task

urlpatterns = [
    # 关闭注册入口，改为django admin创建用户
    # path('register/', views.RegisterView.as_view()),
    path('login/', obtain_jwt_token),
    path('list/', views.UserView.as_view()),
    re_path(r'^auto_run_testsuite_pk/$', timer_task.auto_run_testsuite_pk, name='auto_run_testsuite_pk'),
]
