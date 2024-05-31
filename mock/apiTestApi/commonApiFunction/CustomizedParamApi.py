#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by Liber in 2020-3-3 09:40

import json

import xmltodict


class JsonXmlApi(object):
    """
    xml和json转换方法
    """

    @classmethod
    def json_data_filling(cls, json_data):
        """
        遍历json数据，如value不为dict数据类型，则直接填充数据；如value为dict数据类型，则使用递归方式(调用函数本身)
        继续遍历该key的值，直到value的数据类型不为dict，则开始填充数据；
        :param json_data: 入参的数据必须为dict数据类型
        :return: 返回修改过的入参数据
        """
        for key, value in json_data.items():
            if isinstance(json_data[key], dict):
                cls.json_data_filling(json_data[key])
            else:
                json_data[key] = "<![CDATA[" + ('' if value is None else str(value)) + "]]>"
        return json_data

    @classmethod
    def json_to_data_xml(cls, json_param):
        json_param = json_param if isinstance(json_param, dict) else json.loads(json_param)

        params = cls.json_data_filling(json_param)
        try:
            if 'xml' in json_param or 'response' in params:
                xml_param = xmltodict.unparse(params, encoding='utf-8')
            else:
                xml_param = xmltodict.unparse({'xml': params}, encoding='utf-8')
            xml_param = xml_param.replace('&lt;', '<').replace('&gt;', ">")\
                .replace("amp;", "").replace('&nbsp;', ' ')
            return xml_param
        except Exception as e:
            return False

    @staticmethod
    def xml_to_json(xml_str_param, key=None):
        """
        :param xml_str_param:
        :param key:
        :return:
        """
        try:
            json_param = xmltodict.parse(xml_str_param, encoding='utf-8')
            tran_json = json_param[key] if key else json_param
        except Exception as e:
            tran_json = False
        return json.loads(json.dumps(tran_json)) if tran_json else tran_json

    @staticmethod
    def json_to_xml(json_param, xml=True, full_document=False, **kwargs):
        try:
            if xml:
                xml_json = {'xml': json_param}
            else:
                xml_json = json_param
            xml_param = xmltodict.unparse(xml_json, encoding='utf-8', full_document=full_document, **kwargs)
            return xml_param
        except Exception as e:
            return False

    @staticmethod
    def json_dump(data):
        return json.dumps(data, sort_keys=True, indent=3,
                          separators=(',', ':'), ensure_ascii=False)


