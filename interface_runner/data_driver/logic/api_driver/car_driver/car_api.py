#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.common.base import MyRequests, GetEnvInfo, GetApiUrl
logger = GetLog().logger()  # 引入日志模块

"""
汽车商城项目
"""


class CarApi:
    def __init__(self,os_type,terminalType):
        self.host = GetEnvInfo().car_BYD_mini_host()
        self.get_url = GetApiUrl()
        self.req = MyRequests()
        #self.session = self.req.session()
        self.headers = {
                            "Content-Type": "application/json;charset=UTF-8",
                            "terminalType":terminalType,
                            "os_type":os_type
                       }



    def car_BYD_mini_login(self, phone, smsCode,captcha):
        url = self.get_url.get_car_BYD_api_url("LOGIN", "login_url")
        url_new = self.host + url
        data = {
            "smsCode": smsCode,
            "phone": phone,
            "captcha": captcha
        }
        status_code,text = self.req.post(url=url_new, data=data, headers=self.headers)
        logger.info("BYD汽车商城登录response：{}".format(text))
        return status_code, text



if __name__ == "__main__":
    s = CarApi("MiniApp","MiniApp")
    result = s.BYD_car_mini_login("19999900040", "111111","120c83f760a8c31e4ff")
    print(result)
