# !/usr/bin/python3
# -*- coding: utf-8 -*-
from .base import *
from FasterRunner.utils.projectPath import path_project
DEBUG = False

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'HOST': '10.101.42.80',
#         'NAME': 'autoplate',  # 新建数据库名
#         'USER': 'root',  # 数据库登录名
#         'PASSWORD': '123456',  # 数据库登录密码
#         'OPTIONS': {'charset': 'utf8'},
#         'TEST': {
#             # 'MIRROR': 'default',  # 单元测试时,使用default的配置
#             # 'DEPENDENCIES': ['default']
#         }
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fastuser',  # 新建数据库
        'HOST': '10.101.42.80',
        'CONN_MAX_AGE': 5,
        'USER': 'root',  # 数据库登录名
        'PASSWORD': '123456',  # 数据库登录密码
        'OPTIONS': {'charset': 'utf8'},
        # 单元测试数据库
        'TEST': {
            'NAME': 'test_fast_last',  # 测试过程中会生成名字为test的数据库,测试结束后Django会自动删除该数据库
        }
    },
    'perform': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'perform',  # 新建数据库
        'HOST': '10.101.42.80',
        'CONN_MAX_AGE': 5,
        'USER': 'root',  # 数据库登录名
        'PASSWORD': '123456',  # 数据库登录密码
        'OPTIONS': {'charset': 'utf8mb4'},
        # 单元测试数据库
        'TEST': {
            'NAME': 'perform-test',  # 测试过程中会生成名字为test的数据库,测试结束后Django会自动删除该数据库
        }
    },
    'version_release': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'version_release',  # 新建数据库
        'HOST': '10.101.42.80',
        'CONN_MAX_AGE': 5,
        'USER': 'root',  # 数据库登录名
        'PASSWORD': '123456',  # 数据库登录密码
        'OPTIONS': {'charset': 'utf8mb4'},
        # 单元测试数据库
        'TEST': {
            'NAME': 'version_release-test',  # 测试过程中会生成名字为test的数据库,测试结束后Django会自动删除该数据库
        }
    },
    'interface_runner': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'interface_runner',  # 新建数据库
        'HOST': '10.101.42.80',
        'CONN_MAX_AGE': 5,
        'USER': 'root',  # 数据库登录名
        'PASSWORD': '123456',  # 数据库登录密码
        'OPTIONS': {'charset': 'utf8mb4'},
        # 单元测试数据库
        'TEST': {
            'NAME': 'interface_runner-test',  # 测试过程中会生成名字为test的数据库,测试结束后Django会自动删除该数据库
        }
    },
    'mock': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mock',  # 新建数据库
        'HOST': '10.101.42.80',
        'CONN_MAX_AGE': 5,
        'USER': 'root',  # 数据库登录名
        'PASSWORD': '123456',  # 数据库登录密码
        'OPTIONS': {'charset': 'utf8mb4'},
        # 单元测试数据库
        'TEST': {
            'NAME': 'mock-test',  # 测试过程中会生成名字为test的数据库,测试结束后Django会自动删除该数据库
        }
    },
    'rbac': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rbac',  # 新建数据库
        'HOST': '10.101.42.80',
        'CONN_MAX_AGE': 5,
        'USER': 'root',  # 数据库登录名
        'PASSWORD': '123456',  # 数据库登录密码
        'OPTIONS': {'charset': 'utf8mb4'},
        # 单元测试数据库
        'TEST': {
            'NAME': 'rbac-test',  # 测试过程中会生成名字为test的数据库,测试结束后Django会自动删除该数据库
        }
    },
    'quality': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'quality',  # 新建数据库
        'HOST': '10.101.42.80',
        'CONN_MAX_AGE': 5,
        'USER': 'root',  # 数据库登录名
        'PASSWORD': '123456',  # 数据库登录密码
        'OPTIONS': {'charset': 'utf8mb4'},
        # 单元测试数据库
        'TEST': {
            'NAME': 'quality-test',  # 测试过程中会生成名字为test的数据库,测试结束后Django会自动删除该数据库
        }
    },
}

BROKER_URL = 'redis://127.0.0.1:6379/1'

JMT_SALT = '/data/salt/jmt'

# influxdb 数据库信息
INFLUXDB_TAGS_HOST = '10.71.32.204'
INFLUXDB_HOST = '10.71.32.204'
INFLUXDB_PORT = 8090
INFLUXDB_USER = 'admin'
INFLUXDB_PASSWORD = '123456'
INFLUXDB_DATABASE = 'jmeter'
INFLUXDB_TIMEOUT = 10

INTERFACE_REPORT_PATH_PRO=os.path.join(path_project,'interface_runner','static',"reportWorkDir")
INTERFACE_SUITE_PATH_PRO=os.path.join(path_project, "tempWorkDir", "FasterRunnerRunTests")

