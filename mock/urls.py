from django.conf.urls import url
from mock import views
urlpatterns = [
    # mock 接口数据
    url(r'^add$', views.add_mock),
    url(r'^updata$', views.modify_mock),
    url(r'^delete$', views.del_mock),
    url(r'^update$', views.modify_mock),
    url(r'^info$', views.get_mock_info),
    url(r'^query$', views.get_mock_list),
    url(r'^interface/(?P<interface>\w+)', views.get_mock_data),
    url(r'^condition/add$', views.add_mock_condition),
    url(r'^condition/delete$', views.del_mock_condition),
    url(r'^condition/update$', views.modify_mock_condition),
    url(r'^condition/info$', views.get_mock_condition_check),
    url(r'^condition/list$', views.get_mock_condition_list),
    ]