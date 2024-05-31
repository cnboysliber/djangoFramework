#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.common.base import MyRequests, GetEnvInfo, GetApiUrl

logger = GetLog().logger()  # 引入日志模块

"""
运营后台-中台所有接口
"""


class SceneApi:
    def __init__(self,terminalType=None):
        self.host = GetEnvInfo().scene_host()
        self.get_url = GetApiUrl()
        self.req = MyRequests()
        self.session = self.req.session()
        self.headers = {
                            "Content-Type": "application/json;charset=UTF-8",
                            "isCheckNetEaseCaptcha":"dfsf",  #跳过滑块验证
                            "terminalType":terminalType,
                            "validate":"dsfsd"
                       }



    def scene_login(self, username, password,pushId):
        url = self.get_url.get_scent_api_url("LOGIN", "login_url")
        url_new = self.host + url
        data = {
            "password": password,
            "username": username,
            "pushId": pushId
        }
        status_code,text = self.req.session_post(session=self.session, url=url_new, data=data, headers=self.headers)
        logger.info("案场宝登录response：{}".format(text))
        return status_code, text



if __name__ == "__main__":
    s = SceneApi()
    result = s.scene_login("13614785201", "26%5gn#b","120c83f760a8c31e4ff")
    print(result)
