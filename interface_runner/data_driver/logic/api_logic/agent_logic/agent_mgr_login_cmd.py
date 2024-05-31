#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.agent_driver.agent_mgr_api import AgentManagerApi
import jsonpath

__author__ = 'weisha'
__date__ = '2020-11-17'

class AgentMgrLoginCmd():
    def __init__(self):
        self.login = AgentManagerApi()

    def agent_mgr_login_cmd(self, **kwargs):
        result = {}
        status_code, text = self.login.agentMgr_login_api(**kwargs)
        result['status'] = status_code
        result['code']=jsonpath.jsonpath(text,'$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text,'$.data')[0]
        if data !=None:
            result['accessToken'] = jsonpath.jsonpath(text, '$.data.accessToken')[0]
            result['userId'] = jsonpath.jsonpath(text, '$.data.userId')[0]

        return result

if __name__ == '__main__':
    pass
    # from ..api.login_interface_cmd import LoginInterface
    # res = LoginInterface()
    # usr = 'TEST1016'
    # pwd = 'hdb@1234'
    # result = res.agent_mgr_login(username=usr, password=pwd)
    # print(result)

