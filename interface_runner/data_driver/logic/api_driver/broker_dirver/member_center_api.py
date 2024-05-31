#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.common.base import MyRequests ,GetEnvInfo, GetApiUrl

"""
运营后台-会员中心所有接口封装
"""
__author__ = 'weisha'
__date__ = '2020-09-21'

class MemberCenterApi:
    def __init__(self):
        self.host = GetEnvInfo().middleend_host()
        self.request = MyRequests()
        #cookie_str = GetEnvInfo().middle_cookie()
        self.header = {
            "Content-Type": "application/json;charset=UTF-8",
            #"cookie":cookie_str
        }
    """
   获取推荐上限
   """
    def get_recommend_limit(self):
        data  ={}
        url = GetApiUrl().get_broker_api_url("MIDDLE_MEMBER_CENTER", "recommend_limit")
        url_new = self.host + url
        status_code, text = self.request.post(url=url_new, headers=self.header, data=data)
        return status_code, text

    """
      获取被推荐上限、推荐保护期、到访保护期
      :productType：limit_protected  到访保护期
                    broker_recommend_limit  推荐保护期、被推荐上限                     
    """
    def get_select_product_by_type(self, productType):
        data = {
            "productType":productType
        }
        url = GetApiUrl().get_broker_api_url("MIDDLE_MEMBER_CENTER", "selectProductByType")
        url_new = self.host + url
        status_code, text = self.request.post(url=url_new, headers=self.header, data=data)
        return status_code, text

if __name__ == '__main__':
    mem = MemberCenterApi()
    out = mem.get_select_product_by_type("recommended_limit")
    print(out)