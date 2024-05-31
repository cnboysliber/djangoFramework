"""
Django settings for FasterRunner project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import datetime as datetime
import djcelery
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, LDAPSearchUnion

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir))))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

JMT_PATH = '/data/jmt'
COVER_DIR = '/data/tmp/coverage'
JMT_SALT = '/data/salt'
IMAGES_DIR = '/data/files'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e$od9f28jce8q47u3raik$(e%$@lff6r89ux+=f!e1a$e42+#7'
# SECRET_KEY='fvtdbs#bdshs@ghtujc6734vsv$@1edfs@sg4hhf$ghs)dd)'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['*']

DATA_UPLOAD_MAX_MEMORY_SIZE = None

# Token Settings, 30天过期
INVALID_TIME = 60 * 60 * 24 * 3650

# Application definition
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'influxdb_metrics',
    'rest_framework',
    'corsheaders',
    'rest_framework_swagger',
    'drf_yasg',
    'interface_runner',
    'dwebsocket',
    'fastuser',
    'performApp',
    'channels',
    'version_release',
    'mock',
    'rbac',
    'quality_management',
]

WSGI_APPLICATION = 'FasterRunner.wsgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('10.101.42.80', 6379)],
            # "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}

ASGI_APPLICATION = 'FasterRunner.routing.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'interface_runner.utils.middleware.VisitTimesMiddleware',
    'FasterRunner.middleware.RequestMiddleware'
]
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
ROOT_URLCONF = 'FasterRunner.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [os.path.join(BASE_DIR, '../../templates')],
        'DIRS': [os.path.join(BASE_DIR, 'appfront', 'dist'), os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-valid

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'appfront', 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "appfront", "dist", "static"),
    os.path.join(BASE_DIR,"static",os.path.join(BASE_DIR, 'interface_runner', 'static'))
]

REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': ['FasterRunner.auth.DeleteAuthenticator', 'FasterRunner.auth.Authenticator', ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'FasterRunner.auth.MyJWTAuthentication',  # 登录校验token
    ],
    'UNAUTHENTICATED_USER': None,
    'UNAUTHENTICATED_TOKEN': None,
    # json form 渲染
    'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser',
                               'rest_framework.parsers.FormParser',
                               'rest_framework.parsers.MultiPartParser',
                               'rest_framework.parsers.FileUploadParser',
                               ],
    'DEFAULT_PAGINATION_CLASS': 'FasterRunner.pagination.MyPageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ),
}


AUTH_USER_MODEL = 'fastuser.MyUser'

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'FasterRunner.swagger.CustomSwaggerAutoSchema',
    # 基础样式
    'SECURITY_DEFINITIONS': {
        "basic": {
            'type': 'basic'
        },
    },
    # 如果需要登录才能够查看接口文档, 登录的链接使用restframework自带的.
    # 'LOGIN_URL': 'rest_framework:login',
    # 'LOGOUT_URL': 'rest_framework:logout',
    # 'DOC_EXPANSION': None,
    # 'SHOW_REQUEST_HEADERS':True,
    # 'USE_SESSION_AUTH': True,
    # 'DOC_EXPANSION': 'list',
    # 接口文档中方法列表以首字母升序排列
    'APIS_SORTER': 'alpha',
    # 如果支持json提交, 则接口文档中包含json输入框
    'JSON_EDITOR': True,
    # 方法列表字母排序
    'OPERATIONS_SORTER': 'alpha',
    'VALIDATOR_URL': None,
}
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ()

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Content-Disposition',
    'Project'
)
MQ_USER = 'admin'
MQ_PASSWORD = '111111'
HOST = 'localhost'
DB_NAME = 'faster_db'

IM_REPORT_SETTING = {
    'base_url': 'http://192.168.22.19',
    'port': 8000,
    'report_title': '自动化测试报告'
}

djcelery.setup_loader()
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'
# BROKER_URL = 'amqp://username:password@IP:5672//'

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TASK_RESULT_EXPIRES = 7200
CELERYD_CONCURRENCY = 1 if DEBUG else 2
CELERYD_MAX_TASKS_PER_CHILD = 4
CELERYD_FORCE_EXECV = True

SALT_USER = 'saltmaster'
SALT_PASSWORD = 'salt@123456'

AUTH_LDAP_SERVER_URI = "ldap://10.101.30.8:389"

AUTH_LDAP_BIND_DN = "CN=恒大宝,OU=应用系统账号,DC=hdjt,DC=hdad,DC=local"
AUTH_LDAP_BIND_PASSWORD = "1qaz@WSX"
SEARCH_BASE = 'OU=恒大集团,DC=hdjt,DC=hdad,DC=local'

# 根据上面的改动
AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch(
        SEARCH_BASE,
        ldap.SCOPE_SUBTREE,
        '(sAMAccountName=%(user)s)',
    )
)
# 通过组进行权限控制
AUTH_LDAP_GROUP_SEARCH = LDAPSearchUnion(
    LDAPSearch(
        SEARCH_BASE,
        ldap.SCOPE_BASE,
        "(objectClass=*)",
    ),
)

AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

# is_staff:这个组里的成员可以登录；is_superuser:组成员是django admin的超级管理员；is_active:组成员可以登录django admin后台，但是无权限查看后台内容
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": "OU=房车宝集团技术开发中心测试组,OU=房车宝集团技术开发中心,OU=房车宝集团总部,OU=房车宝集团,OU=恒大集团,DC=hdjt,DC=hdad,DC=local",
    "is_superuser": "OU=房车宝集团技术开发中心测试组,OU=房车宝集团技术开发中心,OU=房车宝集团总部,OU=房车宝集团,OU=恒大集团,DC=hdjt,DC=hdad,DC=local",
}

# 请注意这部分
AUTH_LDAP_USER_ATTR_MAP = {
    'username': 'SAMAccountName',  # 请对应login的username
    # 'password': 'password',  # 请对应login的password
    "first_name": "name",
    "email": "mail"
}

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_LDAP_FIND_GROUP_PERMS = True


class Author(object):

    @staticmethod
    def jwt_response_payload_handler(token, user=None, request=None):
        realname = user.first_name or user.username

        def get_ldap_user(username):
            try:
                # 建立连接
                ldapconn = ldap.initialize(AUTH_LDAP_SERVER_URI)
                # 绑定管理账户，用于用户的认证
                ldapconn.simple_bind_s(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)
                search_scope = ldap.SCOPE_SUBTREE  # 指定搜索范围
                search_filter = "(sAMAccountName=%s)" % username  # 指定搜索字段
                ldap_result = ldapconn.search_s(SEARCH_BASE, search_scope, search_filter, None)  # 返回该用户的所有信息，类型列表
                return ldap_result
            except ldap.LDAPError as e:
                print(e)
                return username
        ldap_ret = get_ldap_user(user.username)
        if ldap_ret:
            realname = ldap_ret[0][0].split(',')[0].strip('CN=') or user.username

        return {
            "token": token,
            "id": user.id,
            "username": realname,
            "account": user.username
        }


JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=365),
    'JWT_ALLOW_REFRESH': True,
    'JWT_RESPONSE_PAYLOAD_HANDLER': Author.jwt_response_payload_handler
}

# 为所有的URL提供websocket，如果只是单独的视图需要可以不选
MIDDLEWARE_CLASSES = [
    'dwebsocket.middleware.WebSocketMiddleware'

]
# 可以允许运行时每个单独视图使用websocket
WEBSOCKET_ACCEPT_ALL = False

DATABASE_APPS_MAPPING = {
    'performApp': 'perform',
    'version_release': 'version_release',
    'interface_runner': 'interface_runner',
    'mock': 'mock',
    'rbac': 'rbac',
    'quality_management': 'quality',
}
DATABASE_ROUTERS = ['FasterRunner.middleware.DatabaseAppsRouter']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {  # 日志格式
        # 'standard': {
        #     'format': '%(asctime)s %(filename)s[line:%(lineno)d][%(levelname)s]| %(message)s',   #日志输出格式
        #     'datefmt': '%Y-%m-%d %H:%M:%S'

        'run_case': {
            'format': '%(asctime)s %(filename)s[line:%(lineno)d][%(levelname)s]| %(message)s',  # 日志输出格式
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        # 日志格式
        'verbose': {
            '()': 'FasterRunner.LoggerSetting.DjangoColorsFormatter',
            'format': '%(asctime)s [%(module)s:%(funcName)s [%(lineno)d]] [%(levelname)s] %(message)s'
        },
        'standard': {  # 标准
            '()': 'FasterRunner.LoggerSetting.DjangoColorsFormatter',
            'format': '[%(asctime)s] [%(module)s:%(funcName)s[line:%(lineno)d] [%(levelname)s] %(message)s'
        },
        'request': {  # 标准
            '()': 'FasterRunner.LoggerSetting.DjangoRequestColorsFormatter',
            'format': '[%(asctime)s] [%(module)s:%(funcName)s[line:%(lineno)d] [%(levelname)s] %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs',
                                     'debug-{}.log'.format(datetime.datetime.now().strftime('%Y%m%d'))),
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'scripts_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs',
                                     'run-{}.log'.format(datetime.datetime.now().strftime('%Y%m%d'))),
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 5,
            'formatter': 'standard',  # 输出格式
            'encoding': 'utf-8',
        },
        # 'console': {  # 控制台输出
        #     'level': 'DEBUG',
        #     'class': 'logging.StreamHandler',
        #     'formatter': 'standard',
        # },

        'console': {  # 控制台输出
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },

        'console_case': {  # 控制台输出
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'run_case',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'request_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR,
                                     'logs',
                                     'request-{}.log'.format(datetime.datetime.now().strftime('%Y%m%d'))),
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        # 'scripts_handler': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     # 'filename': os.path.join(BASE_DIR, 'logs/../../logs/run.log'),
        #     'filename': os.path.join(BASE_DIR, 'logs/run.log'),
        #     'maxBytes': 1024 * 1024 * 100,
        #     'backupCount': 5,
        #     'formatter': 'standard',
        #     'encoding': 'utf-8',
        # },

        'case_handler': {  # 默认
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            # 'filename': os.path.join(BASE_DIR, 'logs/../../logs/debug.log'),
            'filename': os.path.join(BASE_DIR, 'logs/run_case-{}.log'.
                                     format(datetime.datetime.now().strftime('%Y%m%d'))),
            'maxBytes': 1024 * 1024 * 50,  # 50M自动清空
            'backupCount': 5,
            'formatter': 'run_case',  # 输出格式
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django_auth_ldap': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django': {
            'handlers': ['console', 'default', 'scripts_handler'],  # 使用上面设置的哪个handlers
            'level': 'INFO',
            'propagate': False
        },
        'FasterRunner.app': {
            'handlers': ['default', 'console'],
            'level': 'INFO',
            'propagate': False
        },
        'django.request': {
            'handlers': ['request_handler', 'console', ],
            'level': 'DEBUG',
            'propagate': False
        },
        'FasterRunner': {
            'handlers': ['scripts_handler', 'console'],
            'level': 'DEBUG',

            'propagate': False
        },
        'run_case': {
            'handlers': ['case_handler'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}