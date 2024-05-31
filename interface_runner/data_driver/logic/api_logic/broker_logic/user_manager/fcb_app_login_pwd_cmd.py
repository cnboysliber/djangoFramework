#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.broker_dirver.broker_app_api import UserManagerApi
import jsonpath

__author__ = 'weisha'
__date__ = '2020-08-24'

class FcbAppLonginPwd():
    def __init__(self,terminalType=None,loginSelection=None):
        self.login = UserManagerApi(terminalType,loginSelection)

    def login_broker_pwd_cmd(self, **kwargs):
        result = {}
        status_code, text = self.login.login_broker_pwd_api(**kwargs)
        result['status'] = status_code
        result['code']=jsonpath.jsonpath(text,'$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text,'$.data')[0]
        if data !=None:
            result =dict(result,**data)
        return result

    def login_customer_pwd_cmd(self, **kwargs):
        result = {}
        status_code, text = self.login.login_customer_code_api(**kwargs)
        result['status'] = status_code
        result['code']=jsonpath.jsonpath(text,'$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text,'$.data')[0]
        if data !=None:
            result =dict(result,**data)
        return result