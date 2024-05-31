# -*- coding:utf-8 -*-
import os


if __name__ == '__main__':
    print(os.path.abspath(__name__))
    os.system('python manage.py celery -A FasterRunner.mycelery beat -l'
              ' debug --settings=FasterRunner.settings.dev')



