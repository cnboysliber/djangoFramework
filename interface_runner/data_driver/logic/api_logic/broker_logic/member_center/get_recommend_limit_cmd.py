#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.broker_dirver.member_center_api import MemberCenterApi
import jsonpath
__author__ = 'weisha'
__date__ = '2020-08-24'

"""
:获取推荐上限
:input
:null
:output：{"拓客"：[todayBefore,totalAfter]}
:todayBefore：每天推荐客户上限
:totalAfter:推荐未到访客户上限
"""

class GetRecommendLimitCmd:
    def __init__(self):
        self.mem = MemberCenterApi()

    def get_recommend_limit_cmd(self):
        result = {}
        status_code, text = self.mem.get_recommend_limit()
        result['status'] = status_code
        result['code'] = jsonpath.jsonpath(text, '$.code')[0]
        result['message'] = jsonpath.jsonpath(text, '$.message')[0]
        data = jsonpath.jsonpath(text, '$.data')

        if data != None:
            user_trpe = jsonpath.jsonpath(text, '$.data[*].type')
            todayBefore = jsonpath.jsonpath(text, '$.data[*].todayBefore')
            totalAfter = jsonpath.jsonpath(text, '$.data[*].totalAfter')
            for i in range (0, len(user_trpe)):
                result[user_trpe[i]] = [todayBefore[i],totalAfter[i]]
        return result

