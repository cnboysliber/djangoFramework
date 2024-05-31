#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.bmp_driver.bmp_mgr_api import BmpManagerApi
import jsonpath

__author__ = 'weisha'
__date__ = '2020-11-12'

class BmpMgrLoginCmd():
    def __init__(self):
        self.login = BmpManagerApi()

    def bmp_mgr_login_cmd(self, **kwargs):
        result = {}
        status_code, text = self.login.bmp_mgr_login_api(**kwargs)
        result['status'] = status_code
        result['code']=jsonpath.jsonpath(text,'$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text,'$.data')[0]
        if data !=None:
            result['accessToken'] = jsonpath.jsonpath(text,'$.data.accessToken')[0]
        return result

if __name__ == '__main__':
    pass
    # from FCB_Auto_Test.reference.api.login_interface_cmd import LoginInterface
    # res = LoginInterface()
    # usr = '131111110'
    # pwd = 'Idr@2019'
    # result = res.bmp_mgr_login(username=usr, password=pwd)
    # print(result)

