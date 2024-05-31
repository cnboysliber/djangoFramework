#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.broker_dirver.member_center_api import MemberCenterApi
import jsonpath

__author__ = 'weisha'
__date__ = '2020-08-24'

"""
:获取推荐保护期天数
:input
:null
:output：
"""

class GetRecommendUnvisitCmd():
    def __init__(self):
        self.mem = MemberCenterApi()

    def get_recommend_unvisit_protect_cmd(self):
        result = {}
        status_code, text = self.mem.get_select_product_by_type("broker_recommend_limit")
        result['status'] = status_code
        result['code'] = jsonpath.jsonpath(text, '$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text, '$.data')[0]
        if data != None:
            limit = jsonpath.jsonpath(data, "$.[?(@.productKey == 'unvisited_days')]")[0]['productValue']
            result['day'] = limit
        else :
            result['day'] = 'error'
        return result


