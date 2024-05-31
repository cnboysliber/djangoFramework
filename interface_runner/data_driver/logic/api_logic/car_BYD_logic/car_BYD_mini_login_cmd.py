#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.car_driver.car_api import CarApi
import jsonpath

__author__ = 'wangxueyi'
__date__ = '2020-11-17'

class CarBYDMiniLoginCmd():
    def __init__(self,os_type,terminalType):
        self.login = CarApi(os_type,terminalType)

    def car_BYD_mini_login_cmd(self, **kwargs):
        result = {}
        status_code, text = self.login.car_BYD_mini_login(**kwargs)
        result['status'] = status_code
        result['code']=jsonpath.jsonpath(text,'$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text,'$.data')[0]
        if data !=None:
            result.update(data)

        return result

if __name__ == '__main__':
    pass

