#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.common.base import MyRequests, GetEnvInfo, GetApiUrl
from interface_runner.data_driver.common.do_logs import GetLog
import hashlib

logger = GetLog().logger()  # 引入日志模块


"""
经纪中心所有接口
"""
__author__ = 'weisha'
__date__ = '2020-08-12'


class UserManagerApi:
    def __init__(self, terminalType=None, loginSelection=None):
        if terminalType == None:
            terminalType = 'Andriod'
        if loginSelection == None:
            loginSelection = '1'
        self.request = MyRequests()
        self.login_header = {
            "Content-Type": "application/json;charset=UTF-8",
            "terminalType": terminalType,
            #"validate": "abc",
            "loginSelection": loginSelection
        }

    # 密码登录接口
    def login_broker_pwd_api(self, phone, pwd, os_type, app_version, os_version,
                             hardware_version, app_uuid, jpushId, lbsCityCode, siteCityCode):
        url = GetApiUrl().get_broker_api_url("LOGIN", "loginUucas")
        host = GetEnvInfo().get_broker_app_host()
        url_new = host + url

        data = {}
        if phone != None:
            data["phone"] = phone
        if pwd != None:
            pwd_md5 = hashlib.md5()
            pwd_md5.update(pwd.encode("utf-8"))
            data["pwd"] = pwd_md5.hexdigest()
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
        if jpushId != None:
            data["jpushId"] = jpushId
        if lbsCityCode != None:
            data["lbsCityCode"] = lbsCityCode
        if siteCityCode != None:
            data["siteCityCode"] = siteCityCode
        status_code, text = self.request.post(url=url_new, headers=self.login_header, data=data)
        return status_code, text

    def get_code_customer(self, phone,typeCode):
        headers={
                "Content-Type": "application/json",
                "validate": "dsfdgdhgfhfgh"
                }
        requestData={
                    "phone":phone,
                    "type":typeCode,
                    "by_voice_code":0
                    }
        url = GetApiUrl().get_customer_api_url("CODE", "getCode")
        host = GetEnvInfo().get_customer_app_host()
        res = self.request.post(url=host+url, headers=headers, data=requestData)
        logger.info("获取验证码response：{}".format(res[1]))
        return res[1]

    def get_check_code_customer(self, phone,typeCode,code):
        headers={"terminalType": "android", "Content-Type": "application/json; charset=utf-8"}
        requestData={
                    "phone":phone,
                    "type":typeCode,
                    "code":code
                    }
        url = GetApiUrl().get_customer_api_url("CODE", "checkCode")
        host = GetEnvInfo().get_customer_app_host()
        res = self.request.post(url=host+url, headers=headers, data=requestData)
        logger.info("校验验证码response：{}".format(res[1]))
        return res[1]


    def login_customer_code_api(self, phone, code, os_type, app_version, os_version, hardware_version, app_uuid, jpushId, lbsCityCode, siteCityCode, registerFrom):
        '''
        验证码登录
        '''
        url = GetApiUrl().get_customer_api_url("LOGIN", "login")
        host = GetEnvInfo().get_customer_app_host()
        url_new = host + url
        data = {
            "code": code,
            "jpushId": jpushId,
            "lbsCityCode": lbsCityCode,
            "phone": phone,
            "registerFrom": registerFrom,
            "siteCityCode": siteCityCode,
            "hardware_version": hardware_version,
            "os_type": os_type,
            "os_version": os_version,
            "app_version": app_version,
            "app_uuid": app_uuid
        }
        status_code, text = self.request.post(url=url_new, headers=self.login_header, data=data)
        logger.info("登录response：{}".format(text))
        return status_code, text


class BrokerRecommendApi:
    def __init__(self, Authorization, unionid, brokerid, terminalType=None):
        if terminalType == None:
            terminalType = 'Andriod'
        self.host = GetEnvInfo().get_app_host()
        self.request = MyRequests()
        self.header = {
            "Content-Type": "application/json;charset=UTF-8",
            "terminalType": terminalType,
            "Authorization": Authorization,
            "validate": "abc",
            "unionid": unionid,
            "brokerid": brokerid
        }

    # 推荐接口
    def recommend_api(self, cstName, mobileNo, certNo, intentionBuildingId,
                      arriveBuildingId, needDetail, planDate, remark):
        data = {}
        url = GetApiUrl().get_broker_api_url("RECOMMEND", "recommendCustomer")
        url_new = self.host + url
        if cstName != None:
            data["cstName"] = cstName
        if mobileNo != None:
            data["mobileNo"] = mobileNo
        if certNo != None:
            data["certNo"] = certNo
        if intentionBuildingId != None:
            data["intentionBuildingId"] = intentionBuildingId
        if arriveBuildingId != None:
            data["arriveBuildingId"] = arriveBuildingId
        if needDetail != {}:
            data["needDetail"] = needDetail
        if planDate != None:
            data["planDate"] = planDate
        if remark != None:
            data["remark"] = remark
        status_code, text = self.request.post(url=url_new, headers=self.header, data=data)
        return status_code, text

    """
    :请求参数:空
    """

    def recommend_count_api(self):
        data = {}
        url = GetApiUrl().get_broker_api_url("RECOMMEND", "recommendCount")
        url_new = self.host + url
        status_code, text = self.request.post(url=url_new, headers=self.header, data=data)
        return status_code, text
