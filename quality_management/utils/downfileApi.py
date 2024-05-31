# -*- coding:utf-8
from urllib.parse import urlparse
from performApp.utils import error as err
from FasterRunner.utils.logging import logger
from FasterRunner.utils.baseRest import RestRequest


class JmRest(object):

    def __init__(self, host='http://qm.fcb.com.cn/'):
        self.req_success = 1
        self._host = host
        self._headers = {'Content-Type': 'application/json'}

    def down_error_log(self, body: dict = None, **kwargs):
        """
        下载脚本/参数化文件
        :param body:
        :param kwargs:
        :return:
        """
        if not body:
            body = {}
        rest = RestRequest(self._host)
        logger.debug(body)
        rest.fetch(f'/organization/', 'GET', **kwargs)
        if not rest.ok:
            logger.error(rest.data)
            raise
        return rest.content