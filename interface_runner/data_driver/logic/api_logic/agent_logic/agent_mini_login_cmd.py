#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.agent_driver.agent_mini_api import AgentMiniApi
import jsonpath

__author__ = 'weisha'
__date__ = '2020-11-17'


class AgentMiniLoginCmd():
    def __init__(self):
        self.login = AgentMiniApi()

    def agent_mgr_login_cmd(self, **kwargs):
        result = {}
        status_code, text = self.login.agent_mini_login_api(**kwargs)
        result['status'] = status_code
        result['code'] = jsonpath.jsonpath(text, '$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text, '$.data')[0]
        if data != None:
            result['token'] = jsonpath.jsonpath(text, '$.data.token')[0]
            result['guid'] = jsonpath.jsonpath(text, '$.data.guid')[0]
            result['brokerId'] = jsonpath.jsonpath(text, '$.data.brokerId')[0]
            result['orgId'] = jsonpath.jsonpath(text, '$.data.orgId')[0]
            result['unionId'] = jsonpath.jsonpath(text, '$.data.unionId')[0]
            result['myPhone'] = jsonpath.jsonpath(text, '$.data.myPhone')[0]
        return result


if __name__ == '__main__':
    pass
    # from FCB_Auto_Test.reference.api.login_interface_cmd import LoginInterface
    #
    # res = LoginInterface()
    # usr = 'QBESMN0064'
    # pwd = '88346245'
    # result = res.agent_mini_login(username=usr, password=pwd)
    # print('result:', result)
