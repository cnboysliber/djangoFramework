#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import hashlib
from interface_runner.data_driver.common.base import GetEnvInfo, MyRequests, GetApiUrl

"""
小程序接口
"""
__author__ = 'weisha'
__date__ = '2020-11-17'

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(ROOT_DIR)


class AgentMiniApi():
    '''
    机构小程序接口封装
    '''

    def __init__(self):
        self.host = GetEnvInfo().agent_mini_host()
        self.url_conf = GetApiUrl()
        self.request = MyRequests()
        self.login_header = {
            "Content-Type": "application/json;charset=UTF-8"
        }

    # 密码登录接口
    def agent_mini_login_api(self, username=None, password=None):
        url = self.url_conf.get_agent_api_url("MINI_LOGIN", "login")
        url_new = self.host + url

        data = {}
        if username != None:
            data["orgAccount"] = username
        if password != None:
            pwd_md5 = hashlib.md5()
            pwd_md5.update(password.encode("utf-8"))
            data["password"] = pwd_md5.hexdigest()

        data["validate"] = '123456'
        status_code, text = self.request.post(url=url_new, headers=self.login_header, data=data)
        return status_code, text


if __name__ == '__main__':
    usr = 'TEST1016'
    pwd = 'hdb@1234'
    res = AgentMiniApi()
    status_code, text = res.agent_mini_login_api(userId=usr, password=pwd)
