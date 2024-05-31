# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys


import time
import signal


app_name = os.path.basename(os.path.abspath(os.path.join(__file__))).split('.')[0]


def start():
    try:
        os.remove('./control.log')
    except Exception:
        pass

    print('create venv ...')
    if not os.path.exists('./venv'):
        os.system('virtualenv --clear -p python3 ./venv >> ./control.log')

    print('install required packages ...')
    os.system('./venv/bin/pip install -q -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ >> '
              './control.log')

    print('start app ...')
    os.system('./venv/bin/python manage.py collectstatic  --noinput --settings=FasterRunner.settings.pro && '
              'nohup ./venv/bin/gunicorn -c gunicorn.py FasterRunner.wsgi:application >> '
              './control.log 2>&1 &')


def restart():
    if os.path.exists('%s.pid' % app_name):
        with open('%s.pid' % app_name, 'r') as f:
            try:
                pid = int(f.read())
                print('pid is %d' % pid)
                os.system('kill -HUP %d' % pid)
            except OSError as e:
                if e.errno == 3:
                    print('no such process')

                print(e)

    else:
        print('pid file not exist')


def stop():
    if os.path.exists('%s.pid' % app_name):
        with open('%s.pid' % app_name, 'r') as f:
            try:
                pid = int(f.read())
                print('pid is %d' % pid)
                os.kill(pid, signal.SIGTERM)
            except OSError as e:
                if e.errno == 3:
                    print('no such process')

                print(e)

    else:
        print('pid file not exist')


if len(sys.argv) != 2:
    print('only accept start/restart/stop as argument')
    exit()

flag = sys.argv[1]

if 'start' == flag:
    start()
elif 'restart' == flag:
    restart()
elif 'stop' == flag:
    stop()
else:
    print('only accept start/restart/stop as argument')
