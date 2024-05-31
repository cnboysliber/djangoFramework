# -*- coding:utf-8 -*-
import os


if __name__ == '__main__':
    print(os.path.abspath(__name__))
    os.system('python manage.py celery -A FasterRunner.mycelery worker -C '
              '--without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo -l'
              ' info --settings=FasterRunner.settings.dev')



