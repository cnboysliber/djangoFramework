# -*- coding: utf-8 -*-
import re
import json
import copy
import datetime
import traceback

import pymysql
import paramiko

from jsonpath_rw import parse

from mock import error as err
from mock.utils import logger
from mock.apiTestApi.commonApiFunction.CustomizedParamApi import JsonXmlApi


def execute_sql(host, port, user, password, database, sql, filters=None):
    exec_data = []
    errmsg = None
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, db=database, charset='utf8')
    except Exception:
        logger.error('数据库连接异常，检查数据库账户密码等信息')
        errmsg = '数据库连接异常，检查数据库账户密码等信息'
        raise err.AppError(400, errmsg)

    try:
        with conn.cursor() as cursor:
            logger.info(str(sql))
            cursor.execute(sql)
            if cursor.description:
                keys = [column[0] for column in cursor.description]
                for row in cursor.fetchall()[:50]:
                    data = []
                    for index, key in enumerate(keys):
                        if filters and key not in filters:
                            continue
                        value = row[index]
                        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                        data.append((key, value))
                    exec_data.append(dict(data))
            rowcount = cursor.rowcount

    except pymysql.err.ProgrammingError:
        logger.error('sql语句异常:{}'.format(traceback.format_exc()))
        errmsg = 'sql语法错误'
    except Exception as e:
        print(traceback.format_exc())
        logger.error(traceback.format_exc())
        errmsg = 'sql执行异常：{}'.format(e)
        conn.rollback()
    finally:
        conn.commit()
        conn.close()

    if errmsg:
        raise err.AppError(400, errmsg)
    return exec_data, rowcount


def str_to_dic(param):
    if not param:
        return False
    try:
        return param if isinstance(param, dict) else json.loads(param)
    except Exception as e:
        print(traceback.format_exc())
        logger.warning(e)
        return False


def search_parameter(input_string, param_parse=r'\${%s}'):
    """
    在给定字符串中查找被parse 包裹的所有参数, 并以列表返回
    :param input_string:        给定用来搜索参数的字符串
    :param param_parse:         正则匹配的规则
    :return:                    参数列表
    """
    if '%s' in param_parse:
        pattern = re.compile(param_parse % '([^${}]*?)')
    else:
        pattern = re.compile(param_parse)
    if not isinstance(input_string, str):
        return []
    param_list = pattern.findall(input_string)
    return param_list


def parse_request_param(result_param, src, checkpoint, place_parse='@copy', contains=r'\(%s\)'):
    param_list = search_parameter(src, r''.join([place_parse, contains]))
    if not param_list:
        return src
    if isinstance(result_param, str):
        try:
            result_param = json.loads(result_param)
        except:
            raise err.AppError(10001, 'json字符串异常： %s' % result_param)

    for param in param_list:
        # 判断取第几个接口的放回值（包括result、headers、request， 默认取返回值）
        parse_param = param.split('|')
        act = {
            'requestHeader': '请求头',
            'requestData': '请求值',
            'resultHeader': '返回头',
            'resultData': '返回值',
            'resultCookie': '返回Cookie'
        }
        key_type = 'requestData' if checkpoint and len(parse_param) == 1 else 'resultData'
        step_num = len(result_param) if not checkpoint else '当前'
        try:
            # @copy(mch_id) 表示取前一个接口返回体的mch_id
            if len(parse_param) == 1:
                request_param = copy.deepcopy(result_param)[-1][key_type]
            # @copy(2|mch_id) 表示取第2个接口返回体的mch_id
            elif len(parse_param) == 2 and parse_param[0].isdigit():
                step_num = int(parse_param[0])
                request_param = result_param[step_num-1][key_type]
            # @copy(requestData|mch_id)、@copy(requestHeader|mch_id) 表示取前一个接口请求体、请求头、返回头的mch_id
            elif len(parse_param) == 2:
                key_type = parse_param[0]
                request_param = result_param[-1][parse_param[0]]
            # 长度为3，@copy(2|requestHeader|mch_id)
            else:
                step_num = parse_param[0]
                key_type = parse_param[1]
                request_param = result_param[int(step_num)-1][parse_param[1]]
        except KeyError:
            raise err.AppError(400, '继承值{}不存在，请仔细确认'.format(param))

        xml_request_param = JsonXmlApi.xml_to_json(request_param, 'xml') \
            if '<xml>' in request_param else JsonXmlApi.xml_to_json(
            request_param)
        if xml_request_param:
            request_param = xml_request_param
        elif str_to_dic(request_param):
            request_param = json.loads(request_param)
        else:
            pass
        parse_param = parse_param[-1]
        js_exp = parse(parse_param)
        male = js_exp.find(request_param)
        try:
            act_value = [match.value for match in male][0]
        except Exception as e:
            not_instr = '第{0}个接口的{1}'.format(step_num, act.get(key_type, key_type))
            print('{0}不存在{2}中!, {1}'.format(parse_param, str(e), not_instr))
            raise err.AppError(400, '{0}不存在{1}中!'.format(parse_param, not_instr))
        to_replace = ''.join([place_parse, '(', param, ')'])
        act_value = act_value if isinstance(act_value, str) else json.dumps(act_value)
        src = src.replace(to_replace, str(act_value))
    return src

