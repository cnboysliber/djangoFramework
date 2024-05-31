from django.conf.urls import url

from .views import ws


urlpatterns = [
    url('ws/terminal/tasks/log/', ws.TaskLogWebsocket.as_asgi()),
]
