#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import logging
from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.logic.api_driver.middleend_driver.middleend_api import MiddleendApi
import jsonpath
logger = GetLog().logger()

__author__ = 'weisha'
__date__ = '2020-09-22'


class MiddleendLoginCmd():
    def __init__(self, ):
        self.api = MiddleendApi()

    def middleend_login_cmd(self, usr, pwd):
        result = {}
        img_code = self.api.get_validate_code()[0]
        # print(img_code)
        key = self.api.get_check_do_key(usr,pwd,img_code)
        status_code, text = self.api.middleend_login(key=key, usr=usr, pwd=pwd, code=img_code)
        result['status'] = status_code
        #result['ut'] = jsonpath.jsonpath(text, '$.ut')[0]
        text_code = jsonpath.jsonpath(text, '$.code')[0]
        result['code'] = text_code

        if int(text_code) == 0:
            result['message'] = 'success'
            result['ut'] = jsonpath.jsonpath(text, '$.ut')[0]
        else:
            result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        return result

    def middleend_login_successful_cmd(self, count, usr, pwd):
        for index in range(1, count+1):
            res = self.middleend_login_cmd(usr, pwd)
            if res['message'] == '图片验证码输入有误':
                logger.warning("图型界面验证失败{}次，系统会自动循环执行10次，直至成功".format(index))
                if index == 10:
                    return res
                else:
                    continue
            elif res['message'] == '该账号连续输入错误密码超过5次，请十分钟后重试':
                logger.warning("失败原因：{}".format(res['message']))
                return res
            elif res['message'] == 'success':
                return res


if __name__ == '__main__':
    login = MiddleendLoginCmd()
    usr = 'HDTyf0001'
    pwd = 'WbA+ENzQtEOOoV8W9lWmJg=='

    res = login.middleend_login_successful_cmd(10, usr, pwd)
    print(res)
