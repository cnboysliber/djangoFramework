import functools
import traceback
from loguru import logger

from django.db import connections
from rest_framework.response import Response
from interface_runner.utils import parser
from FasterRunner.utils.logging import logger
from FasterRunner.utils import baseError as err
from FasterRunner.utils import response


def request_log(level):
    def wrapper(func):
        @functools.wraps(func)
        def inner_wrapper(request, *args, **kwargs):
            try:
                msg_data = "before process request data:\n{data}".format(data=parser.format_json(request.data))
                msg_params = "before process request params:\n{params}".format(
                    params=parser.format_json(request.query_params))
                if level == 'INFO':
                    if request.data:
                        logger.info(msg_data)
                    if request.query_params:
                        logger.info(msg_params)
                elif level == 'DEBUG':
                    if request.data:
                        logger.debug(msg_data)
                    if request.query_params:
                        logger.debug(msg_params)
                result = func(request, *args, **kwargs)
            except err.AppError as e:
                result = response.response_msg(e.code, e.message, False)
            except Exception as e:
                print(traceback.format_exc())
                logger.warning(e)
                result = response.response_msg(500, str(e), False)

            return Response(result) if isinstance(result, dict) else result

        return inner_wrapper

    return wrapper


# ref: django.db.close_old_connections
def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


def handle_db_connections(func):
    def func_wrapper(*args, **kwargs):
        close_old_connections()
        result = func(*args, **kwargs)
        close_old_connections()

        return result

    return func_wrapper
