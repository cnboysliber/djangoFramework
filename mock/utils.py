import sys
import traceback
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from django.http import JsonResponse
from mock.error import AppError, ErrInternal
from FasterRunner.utils.logging import logger


executor = ThreadPoolExecutor(8)


def response_except(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        response = {}
        try:
            response = fn(*args, **kwargs)
        except AppError as e:
            logger.error(traceback.format_exc())
            response['errormsg'] = e.message
            response['Code'] = e.code
            if e.code == 599:
                return JsonResponse(response, safe=False, status=599)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_str = 'Function name: {0}; Error info: {1}: {2}; Traceback: {3}' \
                .format(str(fn.__name__),
                        str(e.__class__.__name__),
                        str(e),
                        str(traceback.extract_tb(exc_tb)))
            logger.error(traceback.format_exc())
            response['errormsg'] = error_str
            response['Code'] = ErrInternal.code

        # 当ucc关闭时，登陆重定向返回的是对象
        if isinstance(response, dict):
            return JsonResponse(response, safe=False)
        else:
            return response

    return wrapped


def except_logging(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            logger.error(traceback.format_exc())
            raise
    return wrapped


