# -*- coding:utf-8 -*-
from __future__ import absolute_import
import os
import sys
_basedir = os.path.abspath(os.path.dirname(__file__))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FasterRunner.settings.pro')

bind = "{ip}:{port}".format(ip='0.0.0.0', port=8000)
# bind = 'unix:///data/FcbAutoPlatformApi/sock/http.sock'
backlog = 2048

workers = 4
worker_connections = 1000
# worker_class = 'uvicorn.workers.UvicornWorker'

max_requests = 0
timeout = 600
pidfile = 'control.pid'
daemon = False



