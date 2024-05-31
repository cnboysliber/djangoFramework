# -*- coding:utf-8 -*-
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from performApp.ws_urls import urlpatterns as ws_urlpatterns

urlpatterns = []
urlpatterns += ws_urlpatterns
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(urlpatterns)),

})
