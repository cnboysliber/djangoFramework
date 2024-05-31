#!/usr/bin/env python
# -*- coding: utf-8 -*-
from interface_runner.data_driver.logic.api_driver.broker_dirver.member_center_api import MemberCenterApi
import jsonpath

__author__ = 'weisha'
__date__ = '2020-08-24'

"""
:获取到访保护期天数
:input
:null
:output：
"""

class GetRecommendVisitCmd():
    def __init__(self):
        self.mem = MemberCenterApi()

    def get_recommend_visit_protect_cmd(self):
        result = {}
        status_code, text = self.mem.get_select_product_by_type("limit_protected")
        result['status'] = status_code
        result['code'] = jsonpath.jsonpath(text, '$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text, '$.data')[0]
        if data != None:
            limit = jsonpath.jsonpath(data, "$..productValue")[0].split('#')
            result['day'] = limit
        return result


