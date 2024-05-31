import copy
import datetime
import functools
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import types
from threading import Thread

import requests
import yaml
from bs4 import BeautifulSoup
# from loguru import logger
from httprunner import HttpRunner, parser, logger
from httprunner.exceptions import FunctionNotFound, VariableNotFound
from requests.cookies import RequestsCookieJar
from requests_toolbelt import MultipartEncoder
from interface_runner.pytest_run.run import RunCase
from interface_runner import models
from interface_runner.utils.prepare import CaseProcessor
from interface_runner.utils.parser import Format
from FasterRunner.settings.base import BASE_DIR

logger.setup_logger('DEBUG')

TEST_NOT_EXISTS = {
    "code": "0102",
    "status": False,
    "msg": "节点下没有接口或者用例集"
}


def is_function(tup):
    """ Takes (name, object) tuple, returns True if it is a function.
    """
    name, item = tup
    return isinstance(item, types.FunctionType)


def is_variable(tup):
    """ Takes (name, object) tuple, returns True if it is a variable.
    """
    name, item = tup
    if callable(item):
        # function or class
        return False

    if isinstance(item, types.ModuleType):
        # imported module
        return False

    if name.startswith("_"):
        # private property
        return False

    return True


class FileLoader(object):

    @staticmethod
    def dump_yaml_file(yaml_file, data):
        """ dump yaml file
        """
        with io.open(yaml_file, 'w', encoding='utf-8') as stream:
            yaml.dump(
                data,
                stream,
                indent=4,
                default_flow_style=False,
                encoding='utf-8',
                allow_unicode=True)

    @staticmethod
    def dump_json_file(json_file, data):
        """ dump json file
        """
        with io.open(json_file, 'w', encoding='utf-8') as stream:
            json.dump(
                data, stream, indent=4, separators=(
                    ',', ': '), ensure_ascii=False)

    @staticmethod
    def dump_python_file(python_file, data):
        """dump python file
        """
        with io.open(python_file, 'w', encoding='utf-8') as stream:
            stream.write(data)

    @staticmethod
    def dump_binary_file(binary_file, data):
        """dump file
        """
        with io.open(binary_file, 'wb', encoding='utf-8') as stream:
            stream.write(data)

    @staticmethod
    def load_python_module(file_path):
        """ load python module.

        Args:
            file_path: python path

        Returns:
            dict: variables and functions mapping for specified python module

                {
                    "variables": {},
                    "functions": {}
                }

        """
        debugtalk_module = {
            "variables": {},
            "functions": {}
        }

        sys.path.insert(0, file_path)
        module = importlib.import_module("debugtalk")
        # 修复重载bug
        importlib.reload(module)
        sys.path.pop(0)

        for name, item in vars(module).items():
            if is_function((name, item)):
                debugtalk_module["functions"][name] = item
            elif is_variable((name, item)):
                if isinstance(item, tuple):
                    continue
                debugtalk_module["variables"][name] = item
            else:
                pass

        return debugtalk_module


def parse_validate_and_extract(list_of_dict: list, variables_mapping: dict, functions_mapping, api_variables: list):
    """
    Args:
        list_of_dict (list)
        variables_mapping (dict): variables mapping.
        functions_mapping (dict): functions mapping.
        api_variables: (list)
    Returns:
        引用传参，直接修改dict的内容，不需要返回
    """

    # 获取api中所有变量的key
    api_variables_key = []
    for variable in api_variables:
        api_variables_key.extend(list(variable.keys()))

    for index, d in enumerate(list_of_dict):
        is_need_parse = True
        # extract: d是{'k':'v'}, v类型是str
        # validate: d是{'equals': ['v1', 'v2']}， v类型是list
        v = list(d.values())[0]
        try:

            # validate,extract 的值包含了api variable的key中，不需要替换
            for key in api_variables_key:
                if isinstance(v, str):
                    if key in v:
                        is_need_parse = False
                elif isinstance(v, list):
                    # v[1]需要统一转换成str类型，否则v[1]是int类型就会报错
                    if key in str(v[1]):
                        is_need_parse = False

            if is_need_parse is True:
                d = parser.parse_data(d, variables_mapping=variables_mapping, functions_mapping=functions_mapping)
                for k, v in d.items():
                    v = parser.parse_string_functions(v, variables_mapping=variables_mapping,
                                                      functions_mapping=functions_mapping)
                    d[k] = v
                list_of_dict[index] = d
        except (FunctionNotFound, VariableNotFound):
            continue


# def load_case_config_info(testcases, debugtalk, name=None, config=None, project=None):
#     """
#     get test case structure
#     testcases: list
#     config: none or dict
#     debugtalk: dict
#     """
#     refs = {
#         "env": {},
#         "def-api": {},
#         "def-testcase": {},
#         "debugtalk": debugtalk
#     }
#
#     testset = {
#         "config": {
#             "name": testcases[-1]["interface_name"],
#             "variables": []
#         },
#         "teststeps": testcases,
#     }
#
#     if config:
#         testset["config"] = config
#
#     if name:
#         testset["config"]["name"] = name
#
#     # 获取当前项目的全局变量
#     global_variables = models.Variables.objects.filter(project=project).all().values("key", "value")
#     all_config_variables_keys = set().union(*(d.keys() for d in testset["config"].setdefault("variables", [])))  #setdefault为如果健不存在字典中，将会添加键值对进入字典
#     global_variables_list_of_dict = []
#     for item in global_variables:
#         if item["key"] not in all_config_variables_keys:   #防止有重复key出现
#             global_variables_list_of_dict.append({item["key"]: item["value"]})
#
#     # 有variables就直接extend,没有就加一个[],再extend
#     # 配置的variables和全局变量重叠,优先使用配置中的variables
#     testset["config"].setdefault("variables", []).extend(global_variables_list_of_dict)  #extend用于在list末尾添加另外一个对象
#     testset["config"]["refs"] = refs
#
#     # 配置中的变量和全局变量合并，配置的variables和全局变量重叠,优先使用配置中的variables
#     variables_mapping = {}
#     if config:
#         for variables in config['variables']:
#             variables_mapping.update(variables)
#
#     # 驱动代码中的所有函数
#     functions_mapping = debugtalk.get('functions', {})
#
#     # 替换extract(save),validate(assert)中的变量和函数，只对value有效，key无效
#     for testcase in testcases:
#         extract: list = testcase.get('extract', [])
#         validate: list = testcase.get('validate', [])
#         api_variables: list = testcase.get('variables', [])
#         parse_validate_and_extract(extract, variables_mapping, functions_mapping, api_variables)
#         parse_validate_and_extract(validate, variables_mapping, functions_mapping, api_variables)
#
#     return testset

def load_case_config_info(config=None, ac_config=None, project=None, debugtalk=None, env_name=None,
                          db_data=None) -> dict:
    """
    get case config
    """
    config_dict = {}
    debugtalk_res = {}

    # 配置中的变量和全局变量合并，配置的variables和全局变量重叠, 优先使用配置中的variables

    if isinstance(config, dict):
        if "variables" in config.keys():
            pass  # 逻辑待补充
    elif isinstance(config, list):
        pass

    # 获取当前项目的全局变量
    # global_variables = models.Variables.objects.filter(project=project).all().values("key", "value")
    env_id = models.Env.objects.get(name=env_name).id
    global_variables = models.Variables.objects.filter(project=project, env_id=env_id).values("key", "value")

    for item in global_variables:
        if item["key"] not in config_dict:  # 防止有重复key出现
            config_dict[item["key"]] = item["value"]
        else:
            logger.info("全局变量或配置变量存在重复key，请检查")

    # 驱动代码中的所有函数
    functions_mapping = debugtalk[0].get('functions', {})
    for fun_key, fun_value in functions_mapping.items():
        debugtalk_res[fun_key] = fun_value()

    config_dict.update(debugtalk_res)  # 代码运行结果以函数名为key放入全局字典
    if config != None:
        config_dict['config'] = config
    if ac_config != None:
        config_dict['ac_config'] = ac_config
    config_dict['db_config'] = db_data
    config_dict['env'] = env_name

    return config_dict


def load_debugtalk(project):
    """import debugtalk.py in sys.path and reload
        project: int
    """
    # debugtalk.py
    code = models.Debugtalk.objects.get(project__id=project).code

    # file_path = os.path.join(tempfile.mkdtemp(prefix='FasterRunner'), "debugtalk.py")
    tempfile_path = tempfile.mkdtemp(
        prefix='FasterRunner', dir=os.path.join(
            BASE_DIR, 'tempWorkDir'))
    file_path = os.path.join(tempfile_path, 'debugtalk.py')
    os.chdir(tempfile_path)
    try:
        FileLoader.dump_python_file(file_path, code)
        debugtalk = FileLoader.load_python_module(os.path.dirname(file_path))

        os.chdir(BASE_DIR)
        shutil.rmtree(os.path.dirname(file_path))  # 删除指定目录及下面的所有文件
        return debugtalk, file_path

    except Exception as e:
        os.chdir(BASE_DIR)
        shutil.rmtree(os.path.dirname(file_path))


# def debug_suite(suite, project, obj, config=None, save=True, user=''):
#     """debug suite
#            suite :list
#            pk: int
#            project: int
#     """
#     if len(suite) == 0:
#         return TEST_NOT_EXISTS
#
#     debugtalk = load_debugtalk(project)
#     debugtalk_content = debugtalk[0]
#     debugtalk_path = debugtalk[1]
#     os.chdir(os.path.dirname(debugtalk_path))
#     test_sets = []
#     try:
#         for index in range(len(suite)):
#             # copy.deepcopy 修复引用bug
#             # testcases = copy.deepcopy(load_case_config_info(suite[index], debugtalk, name=obj[index]['name'], config=config[index]))
#             testcases = copy.deepcopy(
#                 load_case_config_info(
#                     suite[index],
#                     debugtalk_content,
#                     name=obj[index]['name'],
#                     config=config[index],
#                     project=project
#                 ))
#             test_sets.append(testcases)
#
#         kwargs = {
#             "failfast": False
#         }
#         runner = HttpRunner(**kwargs)
#         runner.run(test_sets)
#         summary = parse_summary(runner.summary)
#
#         if save:
#             save_summary(f"批量运行{len(test_sets)}条用例", summary, project, type=1, user=user)
#         return summary
#
#     except Exception as e:
#         raise SyntaxError(str(e))
#     finally:
#         os.chdir(BASE_DIR)
#         shutil.rmtree(os.path.dirname(debugtalk_path))

def debug_suite(suites, project, ac_config_list, report_name, env_name, project_name, db_data, config_list,
                run_type=1,save=True,user=''):

    """debug suite
           suite :list
           pk: int
           project: int
    """
    test_cases = []
    if len(suites) == 0:
        return TEST_NOT_EXISTS

    try:
        run = RunCase(user,report_name,save)
        for index, suite in enumerate(suites):
            # test_cases = test_cases + suite  # 收集用例信息到一个suit里面运行
            config_data = load_case_config_info(config_list[index], ac_config_list[index], project,
                                                load_debugtalk(project), env_name,
                                                db_data)

            case_data = CaseProcessor().case_info_processor(suite)
            # report_name=run.Make.user_time_num
            report_name=run.report_name
            run.run_main(case_data, config_data, project_name,run_type)

        if save:
            run.run_pytest_dir_gen_report()
            run.run_allure()
        else:
            run.run_pytest_dir()  # 放到一个文件夹下面，统一运行

        return report_name



    # if save:
    #     save_summary(f"批量运行{len(test_sets)}条用例", summary, project, type=1, user=user)
    # return summary

    except Exception as e:
        if run.Make.suit_work_dir:
            shutil.rmtree(run.Make.suit_work_dir)
        logger.log_error(f"debug_suite error: {e}")
        raise SyntaxError(str(e))
    finally:
        pass
        # os.chdir(BASE_DIR)
        # shutil.rmtree(os.path.dirname(debugtalk_path))


# def debug_api(api, project, name=None, config=None, save=True, user=''):
#     """debug api
#         api :dict or list
#         project: int
#     """
#     if len(api) == 0:
#         return TEST_NOT_EXISTS
#
#     # testcases
#     if isinstance(api, dict):
#         """
#         httprunner scripts or teststeps
#         """
#         api = [api]
#
#     # 参数化过滤,只加载api中调用到的参数
#     if config and config.get('parameters'):
#         api_params = []
#         for item in api:
#             params = item['request'].get('params') or item['request'].get('json')
#             for v in params.values():
#                 if type(v) == list:
#                     api_params.extend(v)
#                 else:
#                     api_params.append(v)
#         parameters = []
#         for index, dic in enumerate(config['parameters']):
#             for key in dic.keys():
#                 # key可能是key-key1这种模式,所以需要分割
#                 for i in key.split('-'):
#                     if '$' + i in api_params:
#                         parameters.append(dic)
#         config['parameters'] = parameters
#
#     debugtalk = load_debugtalk(project)
#     debugtalk_content = debugtalk[0]
#     debugtalk_path = debugtalk[1]
#     os.chdir(os.path.dirname(debugtalk_path))
#     try:
#         # testcase_list = [parse_tests(api, load_debugtalk(project), name=name, config=config)]
#         testcase_list = [
#             parse_tests(
#                 api,
#                 debugtalk_content,
#                 name=name,
#                 config=config,
#                 project=project)]
#
#         kwargs = {
#             "failfast": False
#         }
#
#         runner = HttpRunner(**kwargs)
#         runner.run(testcase_list)
#
#         summary = parse_summary(runner.summary)
#
#         if save:
#             save_summary(name, summary, project, type=1, user=user)
#         return summary
#     except Exception as e:
#         logger.error(f"debug_api error: {e}")
#         raise SyntaxError(str(e))
#     finally:
#         os.chdir(BASE_DIR)
#         shutil.rmtree(os.path.dirname(debugtalk_path))


def debug_api(api, project, project_name=None, name=None, report_name="",config=None, save=True, ac_config=None, env_name=None,
              db_data=None, run_type=1,user=None):
    """debug api
        api :dict or list
        project: int
    """
    import traceback
    if len(api) == 0:
        return TEST_NOT_EXISTS

    # testcases
    if isinstance(api, dict):
        """
        httprunner scripts or teststeps
        """
        api = [api]

    if config == "请选择":
        config = None
    if ac_config == "请选择":
        ac_config = None

    # 参数化过滤,只加载api中调用到的参数
    if config and config.get('parameters'):  # 加载config中配置的参数
        api_params = []
        for item in api:
            params = item['request'].get('params') or item['request'].get('json')
            for v in params.values():
                if type(v) == list:
                    api_params.extend(v)
                else:
                    api_params.append(v)
        parameters = []
        for index, dic in enumerate(config['parameters']):
            for key in dic.keys():
                # key可能是key-key1这种模式,所以需要分割
                for i in key.split('-'):
                    if '$' + i in api_params:
                        parameters.append(dic)
        config['parameters'] = parameters

    config_data = load_case_config_info(config, ac_config, project=project, debugtalk=load_debugtalk(project),
                                        env_name=env_name, db_data=db_data)  # 获取全局变量等信息的方法

    try:

        run = RunCase(user,report_name,save)
        case_data = CaseProcessor().case_info_processor(api)
        run.run_main(case_data, config_data, project_name,run_type)

        if save==True:
            run.run_pytest_dir_gen_report()
            run.run_allure()
        else:
            run.run_pytest_dir()

        return run.report_name

    except Exception as e:
        if run.Make.suit_work_dir:
            shutil.rmtree(run.Make.suit_work_dir)
        logger.log_error(f"debug_api error: {e}")
        raise SyntaxError(str(e))
    finally:
        pass
        # os.chdir(BASE_DIR)
        # shutil.rmtree(os.path.dirname(debugtalk_path))


def debug_api_websocket(api, project, project_name=None, name=None, config=None, save=True, user=''):
    """debug api
        api :dict or list
        project: int
    """
    if len(api) == 0:
        return TEST_NOT_EXISTS

    # testcases
    if isinstance(api, dict):
        """
        httprunner scripts or teststeps
        """
        api = [api]

    # 参数化过滤,只加载api中调用到的参数
    if config and config.get('parameters'):  # 加载config中配置的参数
        api_params = []
        for item in api:
            params = item['request'].get('params') or item['request'].get('json')
            for v in params.values():
                if type(v) == list:
                    api_params.extend(v)
                else:
                    api_params.append(v)
        parameters = []
        for index, dic in enumerate(config['parameters']):
            for key in dic.keys():
                # key可能是key-key1这种模式,所以需要分割
                for i in key.split('-'):
                    if '$' + i in api_params:
                        parameters.append(dic)
        config['parameters'] = parameters

    config_data = load_case_config_info(config, project=project, debugtalk=load_debugtalk(project))  # 获取全局变量等信息的方法

    # try:
    case_data = CaseProcessor().case_info_processor(api)
    output = RunCase().run_main_websocket(case_data, config_data, project_name)

    # except Exception as e:
    #     logger.log_error(f"debug_api error: {e}")
    #     raise SyntaxError(str(e))
    # finally:
    #     pass
    #     # os.chdir(BASE_DIR)
    #     # shutil.rmtree(os.path.dirname(debugtalk_path))
    return output


def load_test(test, project=None):
    """
    format testcase
    """

    try:
        format_http = Format(test['newBody'])
        format_http.parse()
        testcase = format_http.testcase

    except KeyError:
        name = test['body']['interface_name']
        if 'case_name' in test.keys():
            if test["body"]["method"] == "config":
                case_step = models.Config.objects.get(name=test["body"]["interface_name"], project=project)
                testcase = eval(case_step.body)
                if case_step.name != name:
                    testcase['interface_name'] = name
            else:
                case_step = models.CaseSuitInfo.objects.get(id=test['id'])  # 判断如果有传用例id，那么就运行数据库里面的用例信息
                testcase = eval(case_step.body)
                if case_step.case_name != name:
                    testcase['interface_name'] = name
        else:
            # 用例调试但却还没有存库时，走这个逻辑
            if test["body"]["method"] == "config":
                case_step = models.Config.objects.get(name=test["body"]["interface_name"], project=project)
                testcase = eval(case_step.body)
                if case_step.name != name:
                    testcase['interface_name'] = name
            else:
                case_step = models.API.objects.get(id=test['id'])
                testcase = eval(case_step.body)
                if case_step.interface_name != name:
                    testcase['interface_name'] = name

        # name = test['body']['interface_name']

        # if case_step.case_name != name:
        #     testcase['interface_name'] = name

    return testcase


def back_async(func):
    """异步执行装饰器
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

    return wrapper


def parse_summary(summary):
    """序列化summary
    """
    for detail in summary["details"]:

        for record in detail["records"]:

            for key, value in record["meta_data"]["request"].items():
                if isinstance(value, bytes):
                    record["meta_data"]["request"][key] = value.decode("utf-8")
                if isinstance(value, RequestsCookieJar):
                    record["meta_data"]["request"][key] = requests.utils.dict_from_cookiejar(
                        value)

            for key, value in record["meta_data"]["response"].items():
                if isinstance(value, bytes):
                    record["meta_data"]["response"][key] = value.decode(
                        "utf-8")
                if isinstance(value, RequestsCookieJar):
                    record["meta_data"]["response"][key] = requests.utils.dict_from_cookiejar(
                        value)

            if "text/html" in record["meta_data"]["response"]["content_type"]:
                record["meta_data"]["response"]["content"] = BeautifulSoup(
                    record["meta_data"]["response"]["content"], features="html.parser").prettify()

    return summary


def save_summary(name, summary, project, type=2, user=''):
    """保存报告信息
    """
    if "status" in summary.keys():
        return
    if name == "" or name is None:
        name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 　删除用不到的属性
    summary['details'][0].pop('in_out')
    # 需要先复制一份,不然会把影响到debug_api返回给前端的报告
    summary = copy.copy(summary)
    summary_detail = summary.pop('details')


    report = models.Report.objects.create(**{
        "project": models.Project.objects.get(id=project),
        "name": name,
        "type": type,
        "status": summary['success'],
        "summary": json.dumps(summary, ensure_ascii=False),
        "creator": user
    })

    models.ReportDetail.objects.create(summary_detail=summary_detail, report=report)


# @back_async
# def async_debug_api(api, project, name, config=None):
#     """异步执行api
#     """
#     summary = debug_api(api, project, save=False, config=config)
#     save_summary(name, summary, project)  # 收集测试报告信息

@back_async
def async_debug_api(api, project, project_name=None, name=None, config=None, save=False, ac_config=None, env_name=None,
                    db_data=None, user=''):
    """异步执行api
    """
    summary = debug_api(api, project, project_name, name, config, save, ac_config, env_name,
                        db_data, user)
    save_summary(name, summary, project)


# @back_async
# def async_debug_suite(suite, project, report, obj, config=None):
#     """异步执行suite
#     """
#     summary = debug_suite(suite, project, obj, config=config, save=False)
#     save_summary(report, summary, project)

@back_async
def async_debug_suite(suite, project, ac_config_list, report_name,env_name, project_name,db_data,config_list,save=False,user=''):
    """异步执行suite,
    """
    summary = debug_suite(suite, project, ac_config_list, report_name,env_name, project_name,db_data,config_list,save,user)
    save_summary(report_name, summary, project)
