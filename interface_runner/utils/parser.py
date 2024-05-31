import datetime
import json

import json5
import time

import requests
import tornado
from tornado import ioloop, httpclient
from enum import Enum

from loguru import logger

from interface_runner import models
from interface_runner.utils.tree import get_tree_max_id, get_all_ycatid, get_tree_ycatid_mapping


class FileType(Enum):
    """
    文件类型枚举
    """
    string = 1
    int = 2
    float = 3
    bool = 4
    list = 5
    dict = 6
    file = 7


class Format(object):
    """
    解析标准HttpRunner脚本 前端->后端
    """

    def __init__(self, body, level='test'):
        """
        body => {
                    header: header -> [{key:'', value:'', desc:''},],
                    request: request -> {
                        form: formData - > [{key: '', value: '', type: 1, desc: ''},],
                        json: jsonData -> {},-
                        params: paramsData -> [{key: '', value: '', type: 1, desc: ''},]
                        files: files -> {"fields","binary"}
                    },
                    extract: save -> [{key:'', value:'', desc:''}],
                    assert: assert -> [{expect: '', actual: '', comparator: 'equals', type: 1},],
                    variables: variables -> [{key: '', value: '', type: 1, desc: ''},],
                    hooks: hooks -> [{setup: '', teardown: ''},],
                    url: url -> string
                    method: method -> string
                    name: name -> string
                }
        """
        try:
            # body['header']={'header':{'token':'111111'}}
            self.__headers = body['header'].pop('header')
            self.__params = body['request']['params'].pop('params')
            self.__data = body['request']['form'].pop('data')
            self.__json = body['request'].pop('json')
            self.__files = body['request']['files'].pop('files')
            self.__variables = body['variables'].pop('variables')
            self.__setup_hooks = body['hooks'].pop('setup_hooks')
            self.__teardown_hooks = body['hooks'].pop('teardown_hooks')

            self.__desc = {
                "header": body['header'].pop('desc'),
                "data": body['request']['form'].pop('desc'),
                "files": body['request']['files'].pop('desc'),
                "params": body['request']['params'].pop('desc'),
                "variables": body['variables'].pop('desc'),

            }

            if level == 'test':
                self.interface_name = body.pop('interface_name')
                self.interface_path = body.pop('interface_path')
                self.method = body.pop('method')
                if 'env_id' in body.keys():
                    self.env_id = body.pop['env_id']

                self.__times = body.pop('times')
                self.__save = body['save'].pop('save')
                self.__assert = body['assert'].pop('assert')
                self.__auto_product = body['auto_product'].pop('auto_product')
                self.__before_sql = body['before_sql'].pop('before_sql')
                self.__execute_sql = body['execute_sql'].pop('execute_sql')
                self.__expect_sql_result = body['expect_sql_result'].pop('expect_sql_result')

                self.__desc["auto_product"] = body['auto_product'].pop('desc')
                self.__desc['save'] = body['save'].pop('desc')
                self.__desc["before_sql"] = body['before_sql'].pop('desc')
                self.__desc["execute_sql"] = body['execute_sql'].pop('desc')
                self.__desc["expect_sql_result"] = body['expect_sql_result'].pop('desc')

            elif level == 'config':
                self.name = body.pop("name")  # 兼容配置页面的保存
                self.env_id = body.pop('env_id')
                self.base_url = body.pop('base_url')
                if 'is_default' in body.keys():  # 加判断逻辑
                    self.is_default = body.pop('is_default')
                self.__parameters = body['parameters'].pop('parameters')

            self.__level = level
            self.testcase = None

            self.project = body.pop('project')
            self.relation = body.pop('nodeId')  # 这里和下面的逻辑故意这样处理，若没有值，下方的parse方法会重新给它们赋值

            # FastRunner的API没有rig_id字段,需要兼容
            self.rig_id = body['rig_id'] if body.get('rig_id') else None
            self.rig_env = body['rig_env'] if body.get('rig_env') else 0

        except KeyError:
            # project or relation
            pass

    def parse(self):
        """
        返回标准化HttpRunner "desc" 字段运行需去除,前端->后端
        """
        if not hasattr(self, 'rig_id'):
            self.rig_id = None

        if not hasattr(self, 'rig_env'):
            self.rig_env = 0

        if self.__level == 'test':
            test = {
                "interface_name": self.interface_name,
                "rig_id": self.rig_id,
                "wait": 0,  # 默认值为0
                "times": self.__times,
                "request": {
                    "interface_path": self.interface_path,
                    "method": self.method,
                    "verify": False
                },
                "desc": self.__desc,  # 把desc提取出来，放在一个字典里面，字典里面是对应每个key，如header、save
                "before_sql": {},
                "execute_sql": {},
                "expect_sql_result": {}
            }

            if self.__save != None:
                test["save"] = self.__save
            if self.__assert != None:
                test['assert'] = self.__assert
            if self.__auto_product != None:
                test['auto_product'] = self.__auto_product
            if self.__before_sql != None:
                test['before_sql'] = self.__before_sql
            if self.__execute_sql != None:
                test['execute_sql'] = self.__execute_sql
            if self.__expect_sql_result != None:
                test['expect_sql_result'] = self.__expect_sql_result


        elif self.__level == 'config':
            test = {
                "name": self.name,
                "env_id": self.env_id,
                "request": {
                    "base_url": self.base_url,
                },
                "desc": self.__desc
            }

            if self.__parameters:
                test['parameters'] = self.__parameters

        if self.__headers:
            test["request"]["header"] = self.__headers
        if self.__params:
            test["request"]["params"] = self.__params
        if self.__data:
            test["request"]["data"] = self.__data
        if self.__json:
            test["request"]["json"] = self.__json
        # 兼容一些接口需要传空json
        if self.__json == {}:
            test["request"]["json"] = {}
        if self.__files:
            test["request"]["files"] = self.__files
        if self.__variables:
            test["variables"] = self.__variables
        if self.__setup_hooks:
            test['setup_hooks'] = self.__setup_hooks
        if self.__teardown_hooks:
            test['teardown_hooks'] = self.__teardown_hooks

        self.testcase = test


class Parse(object):
    """
    标准HttpRunner脚本解析至前端 后端->前端
    """

    def __init__(self, body, level='test'):
        """
        body: => {
                "name": "get token with $user_agent, $os_platform, $app_version",
                "request": {
                    "url": "/api/get-token",
                    "method": "POST",
                    "header": {
                        "app_version": "$app_version",
                        "os_platform": "$os_platform",
                        "user_agent": "$user_agent"
                    },
                    "json": {
                        "sign": "${get_sign($user_agent, $device_sn, $os_platform, $app_version)}"
                    },
                    "save": [
                        {"token": "content.token"}
                    ],
                    "assert": [
                        {"eq": ["status_code", 200]},
                        {"eq": ["header.Content-Type", "application/json"]},
                        {"eq": ["content.success", true]}
                    ],
                    "setup_hooks": [],
                    "teardown_hooks": []
                }
        """
        self.interface_name = body.get('interface_name')
        self.__request = body.get('request')  # header files params json data
        self.__variables = body.get('variables')
        self.__setup_hooks = body.get('setup_hooks', [])
        self.__teardown_hooks = body.get('teardown_hooks', [])
        self.__desc = body.get('desc')

        if level == 'test':
            self.__times = body.get('times', 1)  # 如果导入没有times 默认为1
            self.__save = body.get('save')
            self.__assert = body.get('assert')
            self.__auto_product = body.get('auto_product')

            self.__before_sql = body.get('before_sql')
            self.__execute_sql = body.get('execute_sql')
            self.__expect_sql_result = body.get('expect_sql_result')


        elif level == "config":
            self.__parameters = body.get("parameters")

        self.__level = level
        self.testcase = None

    @staticmethod
    def __get_type(content):
        """
        返回data_type 默认string
        """
        var_type = {
            "str": 1,
            "int": 2,
            "float": 3,
            "bool": 4,
            "list": 5,
            "dict": 6,
        }

        key = str(type(content).__name__)

        # 黑魔法，为了兼容值是int，但又是$引用变量的情况
        if key == 'str' and '$int' in content:
            return var_type['int'], content

        if key in ["list", "dict"]:
            content = json.dumps(content, ensure_ascii=False)
        else:
            content = str(content)
        return var_type[key], content

    def parse_http(self):
        """
        标准前端脚本格式,后端->前端
        """
        init = [{
            "key": "",
            "value": "",
            "desc": ""
        }]

        init_p = [{
            "key": "",
            "value": "",
            "desc": "",
            "type": 1
        }]

        #  初始化test结构
        self.test = {
            "interface_name": self.interface_name,
            "header": init,
            "request": {
                "data": init_p,
                "params": init_p,
                "json_data": ''
            },
            "variables": init_p,
            "hooks": [{
                "setup": "",
                "teardown": ""
            }]
        }

        if self.__level == 'test':
            self.test["times"] = self.__times
            self.test["method"] = self.__request['method']
            self.test["interface_path"] = self.__request['interface_path']
            self.test["assert"] = [{
                "expect": "",
                "actual": "",
                "comparator": "=",
                "type": 1
            }]
            self.test["save"] = init   #给每个字段默认赋值，若为空，前端会不显示输入框
            self.test["auto_product"] = init
            self.test["before_sql"] = init
            self.test["execute_sql"] = init
            self.test["expect_sql_result"] = init

            if self.__save:
                self.test["save"] = []
                for content in self.__save:
                    for key, value in content.items():
                        self.test['save'].append({
                            "key": key,
                            "value": value,
                            "desc": self.__desc["save"][key]
                        })

            if self.__assert:
                self.test["assert"] = []
                for content in self.__assert:
                    for key, value in content.items():
                        obj = Parse.__get_type(value[0])
                        self.test["assert"].append({
                            "expect": value[0],
                            "actual": value[1],
                            "comparator": key,
                            "type": obj[0]
                        })

            self.auto_product_pro(self.__auto_product, 'auto_product')
            self.auto_product_pro(self.__before_sql, 'before_sql')
            self.auto_product_pro(self.__execute_sql, 'execute_sql')
            self.auto_product_pro(self.__expect_sql_result, 'expect_sql_result')
            # if self.__auto_product:
            #     self.test["auto_product"] = []
            #     for content in self.__auto_product:
            #         for key, value in content.items():
            #             self.test['auto_product'].append({
            #                 "key": key,
            #                 "value": value,
            #                 "desc": self.__desc["auto_product"][key]
            #             })



        elif self.__level == "config":
            self.test["base_url"] = self.__request["base_url"]
            self.test["parameters"] = init

            if self.__parameters:
                self.test["parameters"] = []
                for content in self.__parameters:
                    for key, value in content.items():
                        self.test["parameters"].append({
                            "key": key,
                            "value": Parse.__get_type(value)[1],
                            "desc": self.__desc["parameters"][key]
                        })

        if self.__request.get('header'):
            self.test["header"] = []
            for key, value in self.__request.pop('header').items():
                self.test['header'].append({
                    "key": key,
                    "value": value,
                    "desc": self.__desc["header"][key]
                })

        if self.__request.get('data'):
            self.test["request"]["data"] = []
            for key, value in self.__request.pop('data').items():
                obj = Parse.__get_type(value)

                self.test['request']['data'].append({
                    "key": key,
                    "value": obj[1],
                    "type": obj[0],
                    "desc": self.__desc["data"][key]
                })

        # if self.__request.get('files'):
        #     for key, value in self.__request.pop("files").items():
        #         size = FileBinary.objects.get(name=value).size
        #         test['request']['data'].append({
        #             "key": key,
        #             "value": value,
        #             "size": size,
        #             "type": 5,
        #             "desc": self.__desc["files"][key]
        #         })

        if self.__request.get('params'):
            self.test["request"]["params"] = []
            for key, value in self.__request.pop('params').items():
                self.test['request']['params'].append({
                    "key": key,
                    "value": value,
                    "type": 1,
                    "desc": self.__desc["params"][key]
                })

        if self.__request.get('json'):
            self.test["request"]["json_data"] = \
                json.dumps(self.__request.pop("json"), indent=4,
                           separators=(',', ': '), ensure_ascii=False)
        if self.__variables:
            self.test["variables"] = []
            for content in self.__variables:
                for key, value in content.items():
                    obj = Parse.__get_type(value)
                    self.test["variables"].append({
                        "key": key,
                        "value": obj[1],
                        "desc": self.__desc["variables"][key],
                        "type": obj[0]
                    })

        if self.__setup_hooks or self.__teardown_hooks:
            self.test["hooks"] = []
            if len(self.__setup_hooks) > len(self.__teardown_hooks):
                for index in range(0, len(self.__setup_hooks)):
                    teardown = ""
                    if index < len(self.__teardown_hooks):
                        teardown = self.__teardown_hooks[index]
                    self.test["hooks"].append({
                        "setup": self.__setup_hooks[index],
                        "teardown": teardown
                    })
            else:
                for index in range(0, len(self.__teardown_hooks)):
                    setup = ""
                    if index < len(self.__setup_hooks):
                        setup = self.__setup_hooks[index]
                    self.test["hooks"].append({
                        "setup": setup,
                        "teardown": self.__teardown_hooks[index]
                    })
        self.testcase = self.test

    def auto_product_pro(self, input_obj, input_key):
        if input_obj:
            self.test[input_key] = []
            for content in input_obj:
                for key, value in content.items():
                    self.test[input_key].append({
                        "key": key,
                        "value": value,
                        "desc": self.__desc[input_key][key]
                    })


def format_json(value):
    try:
        return json.dumps(
            value, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.warning(e)
        return value


def yapi_properties2json(properties, req_json={}, variables=[], desc={}):
    for field_name, field_value in properties.items():
        value_type = field_value['type']
        if not (value_type == 'array' or value_type == 'object'):
            req_json[field_name] = f'${field_name}'
            variables.append({field_name: field_value.get('default', '')})
            desc[field_name] = field_value['description']
        if value_type == 'array':
            pass

    pass


def format_summary_to_ding(msg_type, summary, report_name=None):
    rows_count = summary['stat']['testsRun']
    pass_count = summary['stat']['successes']
    fail_count = summary['stat']['failures']
    error_count = summary['stat']['errors']
    try:
        # 使用运行环境在配置的report_url
        base_url = summary['details'][0]['in_out']['in']['report_url']
    except KeyError:
        base_url = summary['details'][0]['base_url']
    env_name = '测试' if 'test' in base_url else '生产'
    case_suite_name = summary['details'][0]['name']  # 用例集名称
    # celery执行的报告名
    if report_name:
        case_suite_name = report_name
    start_at = time.strftime(
        '%Y-%m-%d %H:%M:%S',
        time.localtime(
            summary['time']['start_at']))
    duration = '%.2fs' % summary['time']['duration']

    # 已执行的条数
    executed = rows_count
    title = '''自动化测试报告: \n开始执行时间:{2} \n消耗时间:{3} \n环境:{0} \nHOST:{1} \n用例集:{4}'''.format(
        env_name, base_url, start_at, duration, case_suite_name)
    # 通过率
    pass_rate = '{:.2%}'.format(pass_count / executed)

    # 失败率
    fail_rate = '{:.2%}'.format(fail_count / executed)

    fail_count_list = []

    # 失败详情
    if fail_count == 0:
        fail_detail = ''

    else:
        details = summary['details']
        print(details)
        for detail in details:
            for record in detail['records']:
                print(record['meta_data']['validators'])
                if record['status'] != 'failure':
                    continue
                else:
                    response_message = record['meta_data']['response']['json']['info']['message']
                    response_error = record['meta_data']['response']['json']['info']['error']
                    request_url = record['meta_data']['request']['url']
                    case_name = record['name']
                    expect = []
                    check_value = []
                    for validator in record['meta_data']['validators']:
                        expect.append(validator['expect'])
                        check_value.append(validator['check_value'])
                    fail_count_list.append(
                        {
                            'case_name': case_name,
                            'request_url': request_url,
                            'fail_message': f'{response_error} - {response_message}'})

        fail_detail = '失败的接口是:\n'
        for i in fail_count_list:
            s = '用例名:{0}\n PATH:{1}\n  \n'.format(
                i["case_name"], i["fail_message"])
            fail_detail += s

    if msg_type == 'markdown':
        fail_detail_markdown = ''
        report_id = models.Report.objects.last().id
        report_url = f'http://10.0.3.57:8000/api/fastrunner/reports/{report_id}/'
        for item in fail_count_list:
            case_name_and_fail_message = f'> - **{item["case_name"]} - {item["request_url"]} - {item["fail_message"]}**\n'
            fail_detail_markdown += case_name_and_fail_message
        msg_markdown = f"""
                        ## FasterRunner自动化测试报告
                        ### 用例集: {case_suite_name}
                        ### 耗时: {duration}
                        ### 成功用例: {pass_count}个
                        ### 异常用例: {error_count}个
                        ### 失败用例: {fail_count}个
                        {fail_detail_markdown}
                        ### 失败率: {fail_rate}
                        ### [查看详情]({report_url})"""

    else:
        msg = '''{0}
        总用例{1}共条,执行了{2}条,异常{3}条.
        通过{4}条,通过率{5}.
        失败{6}条,失败率{7}.
        {8}'''.format(title, rows_count, executed, error_count, pass_count, pass_rate, fail_count, fail_rate,
                      fail_detail)

    return (msg_markdown, fail_count) if msg_markdown else (msg, fail_count)


# 特殊字段conditions
def set_customized_variable(api_info_template, items):
    if items['type'] == 'object':
        properties: dict = items['properties']
        attr_name: dict = properties['attributeName']
        attribute_name_enum: list = attr_name.get('enum', [''])
        if len(attribute_name_enum) == 0:
            attribute_name_enum = ['']
        target_value: list = [f'${value}' for value in attribute_name_enum]
        # 查询条件字段默认模板
        api_info_template['request']['json']['conditions'] = {
            'attributeName': f'${attribute_name_enum[0]}',
            "rangeType": "$rangeType",
            "targetValue": target_value
        }
        for attr in attribute_name_enum:
            api_info_template['variables']['variables'].append({attr: ''})
            api_info_template['variables']['desc'][attr] = attr_name.get('description', '')

        # 查询条件比较类型
        range_type: dict = properties['rangeType']
        range_type_enum: list = range_type.get('enum', [''])
        api_info_template['variables']['variables'].append({'rangeType': range_type_enum[0]})
        api_info_template['variables']['desc']['rangeType'] = f'条件匹配方式: {",".join(range_type_enum)}'

        # 默认排序
        api_info_template['request']['json']['orderBy'] = [
            {
                "attributeName": f'${attribute_name_enum[0]}',
                "rankType": "DESC"
            }
        ]


class Yapi:
    def __init__(
            self,
            yapi_base_url: str,
            token: str,
            faster_project_id: int):
        self.__yapi_base_url = yapi_base_url
        self.__token = token
        self.fast_project_id = faster_project_id
        self.api_info: list = []
        self.api_ids: list = []
        # self.category_info: list = []
        # api基础信息，不包含请求报文
        self.api_list_url = self.__yapi_base_url + '/api/interface/list'
        # api详情，包含详细的请求报文
        self.api_detail_url = self.__yapi_base_url + '/api/interface/get'
        # api所有分组目录, 也包含了api的基础信息
        self.category_info_url = self.__yapi_base_url + '/api/interface/list_menu'

    def get_category_info(self):
        try:
            res = requests.get(self.category_info_url, params={'token': self.__token}).json()
        except Exception as e:
            logger.error(f"获取yapi的目录失败: {e}")
        finally:
            # {
            #     "errcode": 0,
            #     "errmsg": "成功！",
            #     "data": [
            #         {
            #             "index": 0,
            #             "_id": 3945,
            #             "name": "机台区域管理",
            #             "project_id": 458,
            #             "desc": "",
            #             "uid": 950,
            #             "add_time": 1588490260,
            #             "up_time": 1588490260,
            #             "__v": 0,
            #             "list": [
            #                 {
            #                     "edit_uid": 0,
            #                     "status": "done",
            #                     "index": 0,
            #                     "tag": [],
            #                     "_id": 31573,
            #                     "method": "GET",
            #                     "catid": 3945,
            #                     "title": "查询列表",
            #                     "path": "/woven/base/equipmentArea/query",
            #                     "project_id": 458,
            #                     "uid": 950,
            #                     "add_time": 1588490282,
            #                     "up_time": 1588490541
            #                 }
            #             ]
            #         }
            #     ]
            # }
            if res['errcode'] == 0:
                return res
            else:
                return {
                    "errcode": 1,
                    "errmsg": str(e),
                    "data": []
                }

    def get_api_uptime_mapping(self):
        """
        yapi所有api的更新时间映射关系, {api_id: api_up_time}
        """
        category_info_list = self.get_category_info()
        mapping = {}
        for category_info in category_info_list['data']:
            category_detail = category_info.get('list', [])
            for category in category_detail:
                api_id = category['_id']
                up_time = category['up_time']
                mapping[api_id] = up_time
        return mapping

    def get_category_id_name_mapping(self):
        """
        获取yapi的分组信息映射关系, {category_id: category_name}
        """

        try:
            res = self.get_category_info()
            if res['errcode'] == 0:
                """
                {
            "errcode": 0,
            "errmsg": "成功！",
            "data": [
                {
                "_id": 8409,
                "name": "布行小程序",
                "project_id": 395,
                "desc": 'null',
                "add_time": 1595317970,
                "up_time": 1595317970,
                "list": [
                    {
                        "edit_uid": 0,
                        "status": "undone",
                        "index": 0,
                        "tag": [],
                        "_id": 48205,
                        "title": "查询用户布行信息",
                        "catid": 8409,
                        "path": "/mes/bh/user/listMyFabricStore",
                        "method": "POST",
                        "project_id": 395,
                        "uid": 246,
                        "add_time": 1595317919,
                        "up_time": 1608537377
                        }]
                        }
                    ]
                }
                """
                # {'category_id': 'category_name'}
                category_id_name_mapping = {}
                for category_info in res['data']:
                    # 排除为空的分组
                    if category_info.get('list'):
                        category_name = category_info.get('name')
                        category_id = category_info.get('_id')
                        category_id_name_mapping[category_id] = category_name
                return category_id_name_mapping
        except Exception as e:
            logger.error(f"获取yapi的目录失败: {e}")

    def get_api_info_list(self):
        """
        获取接口列表数据
        """
        try:
            res = requests.get(
                self.api_list_url,
                params={
                    'token': self.__token,
                    'page': 1,
                    'limit': 100000}).json()
            if res['errcode'] == 0:
                """
                {
                    "errcode": 0,
                    "errmsg": "成功！",
                    "data": [
                                'list': [
                                    {
                                         "_id": 4444,
                                         "project_id": 299,
                                         "catid": 1376,
                                         "title": "/api/group/del",
                                         "path": "/api/group/del",
                                         "method": "POST",
                                         "uid": 11,
                                         "add_time": 1511431246,
                                         "up_time": 1511751531,
                                         "status": "undone",
                                         "edit_uid": 0
                                    }
                                ]
                            ]
                }
                """
                return res
        except Exception as e:
            logger.error(f"获取api list失败: {e}")

    def get_api_ids(self):
        """
        获取yapi的api_ids
        """
        api_list = self.get_api_info_list()
        return [api['_id'] for api in api_list['data']['list']]

    def get_batch_api_detail(self, api_ids):
        """
        获取yapi的所有api的详细信息
        """

        api_info = []
        token = self.__token

        i = 0

        # yapi单个api的详情
        """
        {'query_path': {'path': '/mes/utils/customer/retreive',
        'params': []},
        'edit_uid': 0,
        'status': 'undone',
        'type': 'static',
        'req_body_is_json_schema': False,
        'res_body_is_json_schema': True,
        'api_opened': False, 'index': 0, 'tag': [],
        '_id': 8850,
        'method': 'POST',
        'catid': 948,
        'title': '查询客户详情',
        'path': '/mes/utils/customer/retreive',
        'project_id': 395,
        'res_body_type': 'json',
        'desc': '', 'markdown': '', 'req_body_other': '',
        'req_body_type': 'raw',
        'res_body': '{"$schema":"http://json-schema.org/draft-04/schema#","type":"object","properties":{"result":{"type":"object","properties":{"customerNo":{"type":"string"},"factoryNo":{"type":"string"},"fullName":{"type":"string"},"abbrName":{"type":"string"},"province":{"type":"string"},"city":{"type":"string"},"area":{"type":"string"},"address":{"type":"string"},"contactName":{"type":"string"},"contactMobile":{"type":"string"},"description":{"type":"string"},"createTime":{"type":"string"},"createUser":{"type":"string"},"createSystem":{"type":"string"}}},"successful":{"type":"boolean"}}}',
        'uid': 36,
        'add_time': 1560820025,
        'up_time': 1560820411,
        'req_body_form': [], 'req_params': [],
        'req_header': [{'required': '1', '_id': '5d083abb0bdee900010a98b3', 'value': 'application/x-www-form-urlencoded', 'name': 'Content-Type'}, {'required': '1', '_id': '5d083abb0bdee900010a98b2', 'desc': '', 'example': '', 'value': '88F13DF0B2AA4E1188B38E1A5E909AF1', 'name': 'clientId'}, {'required': '1', '_id': '5d083abb0bdee900010a98b1', 'desc': '', 'example': '', 'value': 'AF4649FFA4674ADB873F0C92E7B00227', 'name': 'accessToken'}, {'required': '1', '_id': '5d083abb0bdee900010a98b0', 'desc': '', 'example': '', 'value': 'V2', 'name': 'authen-type'}, {'required': '1', '_id': '5d083abb0bdee900010a98af', 'desc': '', 'example': '', 'value': '74BDB6DA54524D8BAE9C34C04A476019', 'name': 'userId'}],
        'req_query': [{'required': '1', '_id': '5d083abb0bdee900010a98ae', 'desc': '客户编号', 'name': 'customerNo'}], '__v': 0, 'username': 'liucanwen'}
        """
        api_info = []
        err_info = set()

        # def handle_request(response):
        #     try:
        #         res = json.loads(response.body, encoding='utf-8')
        #         api_info.append(res['data'])
        #     except Exception as e:
        #         err_info.add(e)
        #     nonlocal i
        #     i -= 1
        #     if i <= 0:
        #         ioloop.IOLoop.instance().stop()

        # http_client = httpclient.AsyncHTTPClient()
        # for api_id in api_ids:
        #     i += 1
        #     http_client.fetch(
        #         f'{self.api_detail_url}?token={token}&id={api_id}',
        #         handle_request,
        #         method='GET')
        # ioloop.IOLoop.instance().start()
        for api_id in api_ids:
            try:
                res = requests.get(f'{self.api_detail_url}?token={token}&id={api_id}')
                res = json.loads(res.text, encoding='utf-8')
                api_info.append(res['data'])
            except Exception as e:
                err_info.add(e)

        if len(err_info) > 0:
            for err in err_info:
                logger.error(f'err message: {err}')
        return api_info

    def get_variable_default_value(self, variable_type, variable_value):
        if isinstance(variable_value, dict) is False:
            return ''
        variable_type = variable_type.lower()
        if variable_type in ('integer', 'number', 'bigdecimal'):
            return variable_value.get('default', 0)
        elif variable_type == "date":
            return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif variable_type == "string":
            return ""
        return ""

    def create_relation_id(self, project_id):
        category_id_name_mapping: dict = self.get_category_id_name_mapping()
        obj = models.Relation.objects.get(project_id=project_id, type=1)
        eval_tree: list = eval(obj.tree)
        yapi_catids: list = [yapi_catid for yapi_catid in get_all_ycatid(eval_tree, [])]
        if category_id_name_mapping is None:
            return
        for cat_id, cat_name in category_id_name_mapping.items():
            if cat_id not in yapi_catids:
                tree_id = get_tree_max_id(eval_tree)
                base_tree_node = {
                    "id": tree_id + 1,
                    "yapi_catid": cat_id,
                    "label": cat_name,
                    "children": []
                }
                eval_tree.append(base_tree_node)
        obj.tree = json.dumps(eval_tree, ensure_ascii=False)
        obj.save()

    def yapi2faster(self, source_api_info):
        """
        yapi单个api转成faster格式
        """
        api_info_template = {
            "header": {
                "header": {},
                "desc": {}
            },
            "request": {
                "form": {
                    "data": {},
                    "desc": {}
                },
                "json": {},
                "params": {
                    "params": {},
                    "desc": {}
                },
                "files": {
                    "files": {},
                    "desc": {}
                }
            }, "save": {
                "save": [],
                "desc": {}
            }, "assert": {
                "assert": []
            }, "auto_product": {
                "auto_product": [],
                "desc": {}
            },
            "variables": {
                "variables": [],
                "desc": {}
            }, "hooks": {
                "setup_hooks": [],
                "teardown_hooks": []
            }, "interface_path": "", "method": "", "interface_name": "", "times": 1, "nodeId": 0,
            "project": self.fast_project_id,
        }
        default_header = {"accessToken": "$accessToken"}
        default_header_desc = {"accessToken": "登录token"}
        api_info_template['header']['header'].update(default_header)
        api_info_template['header']['desc'].update(default_header_desc)
        # default_validator = {'equals': ['content.successful', True]}  #w的注释
        # api_info_template['assert']['assert'].append(default_validator)

        api_info_template['interface_name'] = source_api_info['title']
        # path中{var}替换成${var}格式
        api_info_template['interface_path'] = source_api_info['path'].replace('{', '${')
        api_info_template['method'] = source_api_info['method']

        # yapi的分组id
        api_info_template['yapi_catid'] = source_api_info['catid']
        api_info_template['yapi_id'] = source_api_info['_id']
        # 十位时间戳
        api_info_template['ypai_add_time'] = source_api_info.get("add_time", "")
        api_info_template['ypai_up_time'] = source_api_info.get("up_time", "")
        # yapi原作者名
        api_info_template['ypai_username'] = source_api_info.get("username", "")

        req_body_type = source_api_info.get('req_body_type')
        req_body_other = source_api_info.get('req_body_other', '')
        if req_body_type == 'json' and req_body_other != '':
            try:
                req_body = json.loads(req_body_other, encoding='utf8')
            except json.decoder.JSONDecodeError:
                # 解析带注释的json
                req_body = json5.loads(req_body_other, encoding='utf8')
            except Exception as e:
                logger.error(
                    f'yapi: {source_api_info["_id"]}, req_body json loads failed: {source_api_info.get("req_body_other", e)}')
            else:
                # TODO: 递归遍历properties所有节点
                if isinstance(req_body, dict):
                    req_body_properties = req_body.get('properties')
                    if isinstance(req_body_properties, dict):
                        for field_name, field_value in req_body_properties.items():
                            field_type = field_value['type']
                            if not (field_type == 'array' or field_type == 'object'):
                                self.set_ordinary_variable(api_info_template, field_name, field_type,
                                                           field_value)
                            if field_type == 'array':
                                items: dict = field_value['items']

                                # 特殊字段处理，通用的查询条件
                                if field_name == 'conditions':
                                    set_customized_variable(api_info_template, items)
                                else:
                                    if items['type'] != 'array' and items['type'] != 'object':
                                        self.set_ordinary_variable(api_info_template, field_name, field_type,
                                                                   field_value)
                            if field_type == 'object':
                                properties: dict = field_value.get('properties')
                                if properties and isinstance(properties, dict):
                                    for property_name, property_value in properties.items():
                                        field_type = property_value['type']
                                        if not (field_type == 'array' or field_type == 'object'):
                                            self.set_ordinary_variable(api_info_template, property_name, field_type,
                                                                       property_value)

        req_query: list = source_api_info.get('req_query', [])
        if req_query:
            for param in req_query:
                param_name = param['name']
                param_desc = param.get('desc', '')
                api_info_template['request']['params']['params'][param_name] = f"${param_name}"
                api_info_template['request']['params']['desc'][param_name] = param_desc
                api_info_template['variables']['variables'].append({param_name: ''})
                api_info_template['variables']['desc'][param_name] = param_desc

        req_params: list = source_api_info.get('req_params', [])
        if req_params:
            for param in req_params:
                # {
                #     "_id": "600155566e7043643b6f1ae2",
                #     "name": "namespace",
                #     "example": "abc123",
                #     "desc": "命名空间"
                # }
                param_name = param['name']
                param_desc = param.get('desc', '')
                param_example = param.get('example', '')
                api_info_template['variables']['variables'].append({param_name: param_example})
                api_info_template['variables']['desc'][param_name] = param_desc

        return api_info_template

    def set_ordinary_variable(self, api_info_template, field_name, field_type, field_value):
        api_info_template['request']['json'][field_name] = f'${field_name}'
        api_info_template['variables']['variables'].append(
            {field_name: self.get_variable_default_value(field_type, field_value)})
        api_info_template['variables']['desc'][field_name] = field_value.get(
            'description', '')

    def get_parsed_apis(self, api_info):
        """
        批量创建faster的api
        """

        apis = [self.yapi2faster(api) for api in api_info]
        proj = models.Project.objects.get(id=self.fast_project_id)
        obj = models.Relation.objects.get(project_id=self.fast_project_id, type=1)
        eval_tree: list = eval(obj.tree)
        tree_ycatid_mapping = get_tree_ycatid_mapping(eval_tree)
        parsed_api = []
        for api in apis:
            format_api = Format(api)
            format_api.parse()
            yapi_catid: int = api['yapi_catid']
            api_body = {
                'interface_name': format_api.interface_name,
                'body': format_api.testcase,
                'interface_path': format_api.interface_path,
                'method': format_api.method,
                'project': proj,
                'relation': tree_ycatid_mapping.get(yapi_catid, 0),
                # 直接从yapi原来的api中获取
                'yapi_catid': yapi_catid,
                'yapi_id': api['yapi_id'],
                'ypai_add_time': api['ypai_add_time'],
                'ypai_up_time': api['ypai_up_time'],
                'ypai_username': api['ypai_username'],
                # 默认为yapi用户
                'creator': 'yapi',
                'type': 2,
            }
            parsed_api.append(models.API(**api_body))
        return parsed_api

    def merge_api(self, parsed_apis, imported_apis):
        """
        合并从yapi获取的api到已经导入测试平台的api
        两种情况：
        1、parsed_api.yapi_id不存在测试平台
        2、yapi的id已经存在测试平台，新获取的parsed_api.ypai_up_time > imported_api.ypai_up_time
        """
        imported_apis_mapping = {api.yapi_id: api.ypai_up_time for api in imported_apis}
        imported_apis_index = {api.yapi_id: index for index, api in enumerate(imported_apis)}

        new_apis = []
        update_apis = []
        imported_apis_ids = set(imported_apis_mapping.keys())
        for api in parsed_apis:
            yapi_id = api.yapi_id
            # 情况1
            if yapi_id not in imported_apis_ids:
                new_apis.append(api)
            else:
                # 情况2
                imported_ypai_up_time = imported_apis_mapping[yapi_id]
                if api.ypai_up_time > int(imported_ypai_up_time):
                    index = imported_apis_index[yapi_id]
                    imported_api = imported_apis[index]
                    imported_api.method = api.method
                    imported_api.name = api.interface_name
                    imported_api.url = api.interface_path
                    imported_api.body = api.body
                    imported_api.ypai_up_time = api.ypai_up_time

                    update_apis.append(imported_api)

        return update_apis, new_apis

    def get_create_or_update_apis(self, imported_apis_mapping):
        """
        返回需要新增和更新的api_id
        imported_apis_mapping: {yapi_id: ypai_up_time}
        新增：
            yapi_id不存在测试平台imported_apis_mapping中
        更新：
            yapi_id存在测试平台imported_apis_mapping, 且up_time大于测试平台的
        """
        api_uptime_mapping: dict = self.get_api_uptime_mapping()

        create_ids = []
        update_ids = []
        for yapi_id, yapi_up_time in api_uptime_mapping.items():
            imported_ypai_up_time = imported_apis_mapping.get(yapi_id)
            if not imported_ypai_up_time:
                # 新增
                create_ids.append(yapi_id)
            elif yapi_up_time > int(imported_ypai_up_time):
                # 更新
                update_ids.append(yapi_id)

        return create_ids, update_ids


class ErrorProcessor:
    '''
    错误信息处理
    '''

    def error_pro(self, error_data: dict) -> str:
        res_str = ""
        for er_key, er_value in error_data.items():
            for value in er_value:
                if res_str == "":
                    res_str = res_str.join((er_key, ":", value))
                else:
                    res_str = res_str.join((er_key, ":", value, ";"))
        return res_str
