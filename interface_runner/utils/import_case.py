import re
import time
from interface_runner.utils.do_excel import DoExcel


# ss = {
#     "interface_name": "获取用户项目列表",
#     "rig_id": "None",
#     "times": 1,
#     "request": {
#         "interface_path": "/hdb-scene-server/appapi/v1/queryProjectListByUserId",
#         "method": "POST",
#         "verify": False,
#         "header": {
#             "Content-Type": "application/json; charset\u003dutf-8",
#             "token": "${ut}",
#             "brokerId": "${userId}",
#             "sign": "${sign}",
#             "timestamp": "${timestamp}",
#             "terminalType": "Android"
#         },
#         "json": {
#             "userId": "${userId}"
#         }
#     },
#     "desc": {
#         "header": {
#             "Content-Type": "",
#             "token": "",
#             "brokerId": "",
#             "sign": "",
#             "timestamp": "",
#             "terminalType": ""
#         },
#         "data": {},
#         "files": {},
#         "params": {},
#         "variables": {},
#         "auto_product": {
#             "phone": "",
#             "num": ""
#         },
#         "save": {
#             "code": "",
#             "code1": ""
#         }
#     },
#     "save": [
#         {
#             "code": "$..code"
#         },
#         {
#             "code1": "$..code1"
#         }
#     ],
#     "assert": [
#         {
#             "\u003d": [
#                 "\u0027000000\u0027",
#                 "$..code"
#             ]
#         },
#         {
#             "\u003d": [
#                 "\u00270000001\u0027",
#                 "$..code1"
#             ]
#         }
#     ],
#     "auto_product": [
#         {
#             "phone": "get_phone(\u0027136\u0027)"
#         },
#         {
#             "num": "get_num"
#         }
#     ]
# }


class CaseSwitchForImportCases():
    '''
    批量导入Excel用例时，转换为可供平台使用的格式数据
    '''

    def __init__(self, file):
        self.file = file

    def case_str_pro(self, str_obj: str,split_tag='='):
        '''
        针对save、autoProduct进行格式转换处理，转换为可供平台存储的数据格式
        :param str_obj:
        :return:
        '''
        if str_obj.strip(' ').replace('\n', '') == '':
            return {}, {}
        else:
            res_desc = {}
            res_list = []
            split_data = str_obj.split(';')
            for data in split_data:
                res_dict = {}
                if data.strip() =='':
                    continue  #为空时，跳过
                if split_tag in data:
                    res = data.split(split_tag)
                    res_dict[res[0].strip(' ').replace('\n', '')] = res[1].strip(' ').replace('\n', '')
                    res_desc[res[0].strip(' ').replace('\n', '')] = ''
                else:
                    res_dict[data.strip(' ').replace('\n', '')] = ''  #兼容autoProduct单独的key，没有value的情况，如china_name
                    res_desc[data.strip(' ').replace('\n', '')] = ''
                res_list.append(res_dict)
            return res_list, res_desc

    def assert_process(self, data: str, key_value: str) -> list:
        '''
        断言切割处理
        :param data:  断言字符串
        :param key_value: 断言key
        :return:
        '''
        res = None
        obj = ["not in", "in"]  # 仅对in类型断言进行处理
        split_list = data.split("$.")
        split_left = split_list[0].replace(" ", "")  # 左边的字符串，去除空格
        split_right = split_list[1].strip()
        if key_value in obj:
            key_value = key_value.replace(" ", "")  # 去空格
            if key_value == "in":  # in断言特殊处理
                if split_left[-1] in ('"', "'"):  # 兼容"$..code"的$前面存在双引号的情况
                    if key_value == split_left[-3:-1]:
                        data = "".join(
                            (split_left[0:-3], key_value.upper(), split_left[-1], '$.', split_right))  # 把分割值转化为大写拼接后再分割
                        res = data.split(key_value.upper())
                        return res
                else:
                    if key_value == split_left[-2:]:
                        data = "".join((split_left[0:-2], key_value.upper(), "$.", split_right))  # 把分割值转化为大写拼接后再分割
                        res = data.split(key_value.upper())
                        return res
            if key_value == "notin":  # notin 断言特殊处理
                if split_left[-1] in ('"', "'"):  # 兼容"$..code"的$前面存在双引号的情况
                    if key_value == split_left[-6:-1]:
                        data = "".join((split_left[0:-6], key_value.upper(), split_left[-1], "$.", split_right))
                        res = data.split(key_value.upper())
                        return res
                else:
                    if key_value == split_left[-5:]:
                        data = "".join((split_left[0:-5], key_value.upper(), "$.", split_right))  # 把分割值转化为大写拼接后再分割
                        res = data.split(key_value.upper())
                        return res
        else:
            res = data.split(key_value)  # 第二次根据key分割
            return res

    def assert_str_pro(self, str_obj):
        '''
        针对assert进行格式转换处理，转换为可供平台存储的数据格式
        :param str_obj:
        :return:
        '''
        if str_obj.strip(' ').replace('\n', '') == '':
            return {}
        else:
            str_obj = str_obj.strip('').replace('\n', '')
            assert_key = ["||", "!=", "=", "not in", "in"]
            res_list = []
            split_obj = str_obj.split(';')
            for data in split_obj:
                for key in assert_key:
                    if key in data:
                        res_dict = {}
                        if key == '||':
                            pass  # 暂时不兼容||断言的情况
                        else:
                            res = self.assert_process(data, key)
                            try:
                                for index,value in enumerate(res):
                                    res[index] = eval(value)
                                res_dict[key]=res
                            except:
                                res_dict[key] = res
                            res_list.append(res_dict)
                            break
            return res_list

    def params_replace(self, str_data, type=0):
        relevant_params = re.findall(r'\${([\s\S]+?)\}', str_data)
        for params_key in relevant_params:
            str_key_list = ['"${' + f"{params_key}" + '}"', "'${" + f'{params_key}' + "}'"]
            n = 0
            for str_key in str_key_list:
                if str_key in str_data:
                    break
                else:
                    n = n + 1
                    if n == 2:  # 若两次都不存在，则认为str_data里面没有加双引号的替换参数，需把替换参数加双引号
                        old_str = "${" + f"{params_key}" + "}"
                        if type == 0:
                            str_data = str_data.replace(old_str, str_key_list[0])
                        elif type == 1:
                            str_data = str_data.replace(old_str, str_key_list[1])

        return str_data

    def params_check(self, str_data: str):
        '''
        针对可替换参数里面的未加双引号的${key}进行处理，替换成加双引号的数据"${key}"
        :param str_data:
        :return:
        '''
        false = False
        true = True
        null = None
        str_data_new = str_data
        try:
            data = eval(str_data)
        except Exception as e:
            try:
                str_data = self.params_replace(str_data, type=0)
                data = eval(str_data)
            except Exception as e:
                str_data = self.params_replace(str_data_new, type=1)
                data = eval(str_data)
        return data

    def header_check(self, str_data):
        '''
        处理请求头里面的多项目登录标识"."，多账号登录标识"_"
        :param str_data:
        :return:
        '''
        str_data = str(self.params_check(str_data))
        relevant_params = re.findall(r'\${([\s\S]+?)\}', str_data)
        new_relevant_params = []
        for key in relevant_params:
            if "_" in key:
                # special_data=["access_token","union_id","broker_id"]
                key = key.split("_")
                if len(key) == 3:
                    key = key[0] + "_" + key[1]
                elif len(key) == 2:
                    if key[1] not in ("token", "id"):  # 不是以这两个结尾，这两个结尾的都是没有加type的
                        key = key[0]
                    else:
                        key = key
                new_relevant_params.append(key)
            else:
                new_relevant_params.append(key)

        for index, key in enumerate(new_relevant_params):
            if "." in key:
                key = key.split(".")[1]
                new_relevant_params[index] = key

        time.sleep(5)

        for new_key in new_relevant_params:
            for key in relevant_params:
                if new_key in key:
                    str_key_list = ['"${' + f"{key}" + '}"', "'${" + f'{key}' + "}'", "${" + f"{key}" + "}"]
                    for str_key in str_key_list:
                        if str_key in str_data:
                            str_data = str_data.replace(str_key, '"${' + f"{new_key}" + '}"')
                            break

        return eval(str_data)

    def header_desc_pro(self, data):
        '''
        给请求头的每个字段赋予描述的空值
        :param data:
        :return:
        '''
        if isinstance(data, str):
            return {}
        else:
            res_dict = {}
            for header_key, header_value in data.items():
                res_dict[header_key] = ''
            return res_dict

    def get_times(self, case_data):
        '''
        次数，转换次数给平台存储
        :param data:
        :return:
        '''
        try:
            if case_data['count'] == '':
                return 1
            else:
                return case_data['count']
        except Exception as e:
            return 1

    def wait_pro(self, case_data: dict):
        try:
            wait_time = case_data['wait']
            if wait_time.strip(' ') == '':
                wait_time = 0
        except Exception as e:
            wait_time = 0

        return wait_time

    def str_replace(self, data, tag=None):
        '''
        把传入的值的中文标点，默认替换为英文标点，以及去空格、换行符
        :param data: 需要替换中文标点的str obj
        :return: data
        '''
        # intab='：；，。！？【】“（）％＃＠＆１２３４５６７８９０'  #中文标点
        # outtab=':;,.!?[]"()%#@&1234567890'  #英文标点
        china_tab = ['：', '；', '，', '。', '！', '？', '【', '】', '“', '（', '）', '％', '＃', '＠', '＆', "’", ' ', '\n', '”']
        english_tab = [':', ';', ',', '.', '!', '?', '[', ']', '"', '(', ')', '%', '#', '@', '&', "'", '', '', '"']
        for index in range(len(china_tab)):
            if china_tab[index] in data:
                if china_tab[index] == tag:
                    if tag == ' ':
                        data = data.strip()
                    else:
                        pass
                else:
                    data = data.replace(china_tab[index], english_tab[index])
        return data

    def case_data_processor(self, case_info):
        '''
        对用例数据进行处理，把字符串里面的中文标点统一替换为英文标点，以及去空格、换行符等
        :param case_info:
        :return:
        '''
        case_info["interfacePath"] = self.str_replace(str(case_info["interfacePath"]))
        case_info["headers"] = self.str_replace(str(case_info["headers"]))
        case_info["autoProduct"] = self.str_replace(str(case_info["autoProduct"]), tag=' ')
        case_info["save"] = self.str_replace(str(case_info["save"]), tag=' ')
        case_info["product"] = self.str_replace(str(case_info["product"]))

        return case_info

    def field_check(self, data: dict, sheet_name: str):
        miss_field_list = []
        must_field = ["interfacePath", "interfaceName", "method", "description", "headers", "body",
                      "autoProduct", "assert", "save", "beforeSql", "executeSql", "expectSqlResult"]
        for must_key in must_field:
            if must_key not in data.keys():
                miss_field_list.append(must_key)
        if len(miss_field_list) != 0:
            return False, f"sheet表：{sheet_name}，缺少必填字段{miss_field_list}"
        else:
            return True, None

    def make_case(self):
        '''
        从Excel里面读取用例，转换为平台可存储的格式
        :return:
        '''
        false = False
        true = True
        null = None
        cases_switch_list = []
        api_template_list = []
        api_interface_path_list = []
        excel_obj = DoExcel(self.file)
        sheet_names = excel_obj.get_sheet_name()
        for sheet_name in sheet_names:
            self.sheet_name = sheet_name
            excel_data = excel_obj.get_listdict_all_value(sheet_name)
            if len(excel_data) != 0:
                field_check_res = self.field_check(excel_data[0], sheet_name)  # 必填字段校验
                if not field_check_res[0]:
                    raise Exception(field_check_res[1])

            for case_data in excel_data:
                add_template_tag = False  # 是否添加到api模板list里面的一个tag标识
                case_data = self.case_data_processor(case_data)  # 针对请求头等字段的中文符号进行处理

                if case_data['interfacePath'] not in api_interface_path_list:
                    api_interface_path_list.append(case_data['interfacePath'])
                    add_template_tag = True

                autoProduct_switch_obj = self.case_str_pro(case_data['autoProduct'])
                save_switch_obj = self.case_str_pro(case_data['save'])
                assert_switch_obj = self.assert_str_pro(case_data['assert'])
                before_sql_switch_obj = self.case_str_pro(case_data['beforeSql'],split_tag=':')
                execute_sql_switch_obj = self.case_str_pro(case_data['executeSql'],split_tag=':')
                expect_sql_result_switch_obj = self.case_str_pro(case_data['expectSqlResult'],split_tag=':')

                description = case_data['description'].replace('\n', '').replace(' ', '')

                case_obj = {
                    "interface_name": f"{case_data['interfaceName']}-{description}",
                    "rig_id": "None",
                    "times": self.get_times(case_data['count']),
                    "wait": self.wait_pro(case_data),
                    "request": {
                        "interface_path": case_data['interfacePath'],
                        "method": case_data['method'],
                        "verify": False,
                        "header": self.header_check(case_data['headers']),
                        "json": self.params_check(case_data['body']),
                    },
                    "desc": {
                        "header": self.header_desc_pro(eval(case_data['headers'])),
                        "data": {},
                        "files": {},
                        "params": {},
                        "variables": {},
                        "auto_product": autoProduct_switch_obj[1],
                        "save": save_switch_obj[1],
                        "before_sql": before_sql_switch_obj[1],
                        "execute_sql": execute_sql_switch_obj[1],
                        "expect_sql_result": expect_sql_result_switch_obj[1],
                    },
                    "save": save_switch_obj[0],
                    "assert": assert_switch_obj,
                    "auto_product": autoProduct_switch_obj[0],
                    "before_sql": before_sql_switch_obj[0],
                    "execute_sql": execute_sql_switch_obj[0],
                    "expect_sql_result": expect_sql_result_switch_obj[0],
                }

                cases_switch_list.append(case_obj)

                if add_template_tag:
                    api_template_list.append(case_obj)

        return cases_switch_list, api_template_list


if __name__ == "__main__":
    file_path = r'E:\ScriptPJ\autoScript\make_case\共享中心后台全部接口用例.xlsx'
    case_obj = CaseSwitchForImportCases(file_path)
    # str_obj="china_name;\nmobileNo=get_phone('1700000')\n;certNo=get_random_num(6)"
    # # str_obj = ''
    # ss = case_obj.case_str_pro(str_obj)
    # print(ss)
    assert_str = "'000000'=$..'code';'111111'!=$..'slet'"
    try:
        ss = case_obj.make_case()
    except Exception as e:
        import traceback

        print(f"sheet表：'{case_obj.sheet_name}' 发生异常，请检查")
        print(traceback.format_exc())
    print(ss)
