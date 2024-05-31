#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.scene_driver.scene_api import SceneApi
import jsonpath

__author__ = 'wangxueyi'
__date__ = '2020-11-17'

class SceneLoginCmd():
    def __init__(self,terminalType):
        self.login = SceneApi(terminalType)

    def scene_bao_login_cmd(self, **kwargs):
        result = {}
        status_code, text = self.login.scene_login(**kwargs)
        result['status'] = status_code
        result['code']=jsonpath.jsonpath(text,'$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text,'$.data')[0]
        if data !=None:
            result['ut'] = jsonpath.jsonpath(text, '$.data.ut')[0]
            result['userId'] = jsonpath.jsonpath(text, '$.data.userId')[0]
            result['userName'] = jsonpath.jsonpath(text, '$.data.userName')[0]
            result['phoneNo'] = jsonpath.jsonpath(text, '$.data.phoneNo')[0]
            result['pushId'] = jsonpath.jsonpath(text, '$.data.pushId')[0]
            result['userRoleName'] = jsonpath.jsonpath(text, '$.data.userRoleName')[0]

        return result

if __name__ == '__main__':
    pass

