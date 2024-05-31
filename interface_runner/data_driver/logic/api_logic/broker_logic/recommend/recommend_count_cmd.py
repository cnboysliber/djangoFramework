#!/usr/bin/env python
# -*- coding: utf-8 -*-

from interface_runner.data_driver.logic.api_driver.broker_dirver.broker_app_api import BrokerRecommendApi
import jsonpath

__author__ = 'weisha'
__date__ = '2020-08-24'

class RecommendCountCmd():
    def __init__(self,Authorization,union_id,brokerid):
        self.rec = BrokerRecommendApi(Authorization, union_id, brokerid)

    def recommend_count_cmd(self):
        result = {}
        status_code, text = self.rec.recommend_count_api()
        result['status'] = status_code
        result['code'] = jsonpath.jsonpath(text, '$.code')[0]
        data = jsonpath.jsonpath(text, '$.data')[0]
        if data != None:
            result = dict(result, **data)
        return result




