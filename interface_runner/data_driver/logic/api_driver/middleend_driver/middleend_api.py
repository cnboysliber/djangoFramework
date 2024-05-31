#!/usr/bin/env python
# -*- coding: utf-8 -*-


from interface_runner.data_driver.common.base import MyRequests, GetEnvInfo, GetApiUrl
from interface_runner.data_driver.common.get_validate_code import GetGraphValidateCode

"""
运营后台-中台所有接口
"""


class MiddleendApi:
    def __init__(self):
        self.host = GetEnvInfo().middleend_host()
        self.get_url = GetApiUrl()
        self.req = MyRequests()
        self.session = self.req.session()
        self.headers = {
            # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8"
            # "Host": "middleend-sit-adminportal.fcb.com.cn"
        }

    def get_validate_code(self):
        param = {
            "width": 100,
            "height": 40,
            "codeCount": 4,
            "codeNmInSession": "vicode"
        }
        val_code = GetGraphValidateCode()
        url = self.get_url.get_middleend_api_url("LOGIN", "get_code_url")
        url_new = self.host + url
        # image = self.req.session_get(session=self.session,url=url_new, data=param, headers=self.headers)
        image = self.req.session_get(session=self.session, url=url_new, data=param, headers=self.headers)
        # print(type(image))
        code = val_code.get_code(image)
        # index = 0
        # print(code)
        while len(code) != 4:
            # image = self.req.session_get(session=self.session,url=url_new, data=param, headers=self.headers)
            image = self.req.session_get(session=self.session, url=url_new, data=param, headers=self.headers)
            code = val_code.get_code(image)
            # index = index + 1
            # print(index)
            # print(code)
        return code, self.session

    # 获取key作为登录入参
    def get_check_do_key(self, user, pwd, code):
        url = self.get_url.get_middleend_api_url("LOGIN", "get_key")
        url_new = self.host + url
        data = {
            "checkImageCode": code,
            "username": user,
            "password": pwd
        }
        text = self.req.session_post(session=self.session, url=url_new, data=data, headers=self.headers)
        return text[1]["data"]["key"]

    def middleend_login(self, key, usr, pwd, code):
        url = self.get_url.get_middleend_api_url("LOGIN", "login_url")
        url_new = self.host + url
        data = {
            "checkImageCode": code,
            "password": pwd,
            "key": key,
            "type": 1,
            "username": usr,
            "verifyCode": ""
        }
        # status_code, text = self.req.session_post(session=self.session,url=url_new, data=data, headers=self.headers)
        status_code, text = self.req.session_post(session=self.session, url=url_new, data=data, headers=self.headers)
        return status_code, text


if __name__ == "__main__":
    s = MiddleendApi()
    code = s.get_validate_code()
    print(code)
    print(type(code))
    result = s.middleend_login("HD001", "abc123456@", code)
    print(result)
