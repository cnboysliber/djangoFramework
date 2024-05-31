#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.bmp_driver.bmp_mini_api import BmpMiniApi
import jsonpath

__author__ = 'weisha'
__date__ = '2020-11-12'

class BmpMiniLoginCmd():
    def __init__(self,):
        self.login = BmpMiniApi()

    def bmp_mini_login_cmd(self, **kwargs):
        result = {}
        status_code, text = self.login.bmp_mini_login_api(**kwargs)
        result['status'] = status_code
        result['code']=jsonpath.jsonpath(text,'$.code')[0]
        # result['message'] = jsonpath.jsonpath(text, '$.data.msg')[0]
        data = jsonpath.jsonpath(text,'$.data')[0]

        if data !=None:
            account_info = jsonpath.jsonpath(text,'$.data.result')[0]
            result =dict(result,**account_info)
        return result

if __name__ == '__main__':
    pass
    # from FCB_Auto_Test.reference.api.login_interface_cmd import LoginInterface
    # res = LoginInterface()
    #
    #
    # usr = '13570841486'
    # pwd = 'heyi1111'
    # ostype = 'MiniApp'
    # result = res.bmp_mini_login(phone=usr, pwd=pwd, os_type=ostype)
    # print(result)

