#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import rsa
import base64
import hashlib
from interface_runner.data_driver.common.base import GetEnvInfo,MyRequests,GetApiUrl

"""
会员经理小程序接口
"""
__author__ = 'weisha'
__date__ = '2020-11-12'

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(ROOT_DIR)

class BmpMiniApi():
    '''
    会员经理平台登录接口封装
    '''
    def __init__(self):
        self.host = GetEnvInfo().bmp_manager_host()
        self.url_conf = GetApiUrl()
        self.request = MyRequests()
        self.login_header = {
            "Content-Type": "application/json;charset=UTF-8"
        }

    # 密码登录接口
    def bmp_mini_login_api(self, phone=None, pwd=None, os_type=None, app_version=None, os_version=None, hardware_version=None, app_uuid=None):
        url = self.url_conf.get_bmp_api_url("MINI_LOGIN", "login")
        url_new = self.host + url

        data = {}
        if phone != None:
            data["phone"] = phone
        if pwd != None:
            pwd_md5 = hashlib.md5()
            pwd_md5.update(pwd.encode("utf-8"))
            pub_key = self.url_conf.get_bmp_api_url("PUBKEY", "mini_pubkey")
            key_load = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key)
            pwd_rsa = rsa.encrypt(pwd_md5.hexdigest().encode('utf-8'), key_load)
            pwd_base64 = base64.b64encode(pwd_rsa).decode()
            data["pwd"] = str(pwd_base64)

        if os_type != None:
            data["os_type"] = os_type
        if app_version != None:
            data["app_version"] = app_version
        if os_version != None:
            data["os_version"] = os_version
        if hardware_version != None:
            data["hardware_version"] = hardware_version
        if app_uuid != None:
            data["app_uuid"] = app_uuid

        # data["password"] = 'igPnNTgQN3ZZ14aqgmIUZOh0ZzRniHVYCYOy2ejpdmBE01rkm88USm5m2WN9jAcKboW8yX60RD10NiEXRLpV647qM1l7F0SluPZnrfaVGf7mdKFKKd7vON+SG7MIiNOulDbHRtZ6qDaytMzaTRKUhhxwmwWu2zp83jpEGrJiERM='
        data["captcha_code"] = '123456'
        status_code, text = self.request.post(url=url_new, headers=self.login_header, data=data)
        return status_code, text

    # def rsa_key(self):
    #     pubkey,privkey = rsa.newkeys(1024)
    #     pub = pubkey.save_pkcs1()
    #     pri = privkey.save_pkcs1('PEM')
    #     with open('pubkey.pem', mode='wb') as f, open('privkey.pem', mode='wb') as f1:
    #         f.write(pub)
    #         f1.write(pri)

if __name__ == '__main__':
    res = BmpMiniApi()
    # code = res.get_validate_code_web()
    # # res.test()
    usr = '13570841486'
    pwd = 'heyi1111'
    ostype = 'MiniApp'
    # dK1Ot6Of6wYMe3kp4by6buNinDOiEt3qzSzyquhvbTqzVlIjO1JjuOpELAboAybD + rNvy / HXRc4Z8uEIVjdE8PgfaOLWNre6mWqJL4QORDm + W5OZfgL2AmcfoUkJKUG1vkLkVNG7zKOFlTnN / lcMj + ypkV / z2bU5hw6JfuFTDH0 =
    # out = res.middlend_login_web(usr, pwd, code)
    # print(out)
    # usr = 'kkk008'
    # pwd = 'hdb@123456'
    # res = AgentManagerApi()

    # out = res.is_login_success()
    # print(out)
    status_code, text = res.bmp_mini_login_api(phone=usr,pwd=pwd,os_type=ostype)
    print(status_code, text)
