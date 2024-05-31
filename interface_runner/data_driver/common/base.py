# coding:utf-8
import os
import re
import jsonpath
import copy
import time
import random
from interface_runner.data_driver.common.data_process import DataProcess
from interface_runner.data_driver.common.do_excel import DoExcel
from interface_runner.data_driver.common.httprequests import HttpRequests
from interface_runner.data_driver.common import do_config
from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.common.data_process import RandomInfo
from interface_runner.data_driver.common.project_path import data_path

logger = GetLog().logger()  # 引入日志模块
ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
publicDict = {}  # 当前模块公共字典


class UserInfo:
    """所有网站的登录账号信息
    description:获取
    """

    def __init__(self):
        env = GetEnvInfo().get_env()
        if env in (None, 'test'):
            self.ex = DoExcel(os.path.join(data_path, 'login_info_test.xlsx'))
            self.mysql_dir = do_config.Config(
                ROOT_PATH + '/config/db/' + 'test_db.cfg')
        elif env == 'uat':
            self.ex = DoExcel(os.path.join(data_path, 'login_info_uat.xlsx'))
            self.mysql_dir = do_config.Config(
                ROOT_PATH + '/config/db/' + 'uat_db.cfg')
        elif env == 'sit2':
            self.ex = DoExcel(os.path.join(data_path, 'login_info_sit2.xlsx'))
            self.mysql_dir = do_config.Config(
                ROOT_PATH + '/config/db/' + 'sit2_db.cfg')
        self.env = env

    # 获取APP c端登录账号信息
    def get_app_customer_login_account(self):
        account = self.ex.get_listdict_all_value('fcb_app_c')
        self.ex.excel_close()
        return account

    # 获取APP b端登录账号信息
    def get_app_broker_login_account(self):
        account = self.ex.get_listdict_all_value('fcb_app_b')
        self.ex.excel_close()
        return account

        # 获取中台登录账号信息

    def get_middleen_login_account(self):
        account = self.ex.get_listdict_all_value('middleend')
        self.ex.excel_close()
        return account

    # 获取推荐楼盘信息
    def get_recommend_buding_id(self):
        building_id = self.ex.get_listdict_all_value('building')
        self.ex.excel_close()
        return building_id

    # 获取机构中台登录账号
    def get_agent_mgr_login_account(self):
        account = self.ex.get_listdict_all_value('agent_mgr')
        self.ex.excel_close()
        return account

    # 获取会员经理中台登录账号
    def get_bmp_mgr_login_account(self):
        account = self.ex.get_listdict_all_value('bmp_mgr')
        self.ex.excel_close()
        return account

    # 获取机构小程序登录账号
    def get_agent_mini_login_account(self):
        account = self.ex.get_listdict_all_value('agent_mini')
        self.ex.excel_close()
        return account

    # 获取会员经理小程序登录账号
    def get_bmp_mini_login_account(self):
        account = self.ex.get_listdict_all_value('bmp_mini')
        self.ex.excel_close()
        return account

    def get_scene_bao_login_account(self):
        account = self.ex.get_listdict_all_value('scene_bao')
        self.ex.excel_close()
        return account

    def get_mingyuan_account(self):
        account = self.ex.get_listdict_all_value('mingyuan')
        self.ex.excel_close()
        return account

    def get_db_account(self):
        account = self.mysql_dir.get_sections()
        return account

    def get_car_BYD_mini_login_account(self):
        account = self.ex.get_listdict_all_value('car_BYD_mini')
        self.ex.excel_close()
        return account


class GetEnvInfo:
    """
    #获取环境配置信息
    """

    def __init__(self):
        self.info = do_config.GetInfo(ROOT_PATH + '/config/' + 'env_info.cfg')
        self.env = self.info.get_info('ENV', 'env')
        self.proxy_host = self.info.get_info('PROXY_HOST', 'proxy_host')
        if self.env in (None, 'test'):
            self.host_model = 'TEST_HOST'
        elif self.env == 'uat':
            self.host_model = 'UAT_HOST'
        elif self.env == 'sit2':
            self.host_model = 'SIT2_HOST'

    def get_env(self):
        return self.env

    def get_broker_app_host(self):
        return self.info.get_info(self.host_model, "fcb_app_host_b")

    def get_customer_app_host(self):
        return self.info.get_info(self.host_model, "fcb_app_host_c")

    def pc_web_host(self):
        return self.info.get_info(self.host_model, "pc_web_host")

    def agent_manager_host(self):
        return self.info.get_info(self.host_model, "agent_manager_host")

    def agent_manager_api(self):
        return self.info.get_info(self.host_model, "agent_manager_api")

    def agent_mini_host(self):
        return self.info.get_info(self.host_model, "agent_mini_host")

    def middleend_host(self):
        return self.info.get_info(self.host_model, "middleend_host")

    def bmp_manager_host(self):
        return self.info.get_info(self.host_model, "bmp_manager_host")

    def bmp_mini_host(self):
        return self.info.get_info(self.host_model, "bmp_mini_host")

    def scene_host(self):
        return self.info.get_info(self.host_model, "scene_host")

    def car_BYD_mini_host(self):
        return self.info.get_info(self.host_model, "car_BYD_mini_host")

    def scene_h5_host(self):
        return self.info.get_info(self.host_model, "scene_host")

    def get_hosts(self):
        '''
        获取所有的host
        '''
        executeDict = {
            "fcb_app": self.info.get_info(self.host_model, "fcb_app_host_b"),
            "fcb_app_b": self.info.get_info(self.host_model, "fcb_app_host_b"),
            "fcb_app_c": self.info.get_info(self.host_model, "fcb_app_host_c"),
            "fcb_h5_c": self.info.get_info(self.host_model, "fcb_h5_host_c"),
            "fcb_h5_b": self.info.get_info(self.host_model, "fcb_h5_host_b"),
            "middleend": self.info.get_info(self.host_model, "middleend_host"),
            "pc": self.info.get_info(self.host_model, "pc_web_host"),
            "om": self.info.get_info(self.host_model, "pc_web_host"),
            "agent_mgr": self.info.get_info(self.host_model, "agent_manager_api"),
            "agent_mini": self.info.get_info(self.host_model, "agent_mini_host"),
            "bmp_mgr": self.info.get_info(self.host_model, "bmp_manager_host"),
            "bmp_mini": self.info.get_info(self.host_model, "bmp_mini_host"),
            "middleend_h5": self.info.get_info(self.host_model, "middleend_h5_host"),
            "scene_bao": self.info.get_info(self.host_model, "scene_host"),
            "scene_bao_h5": self.info.get_info(self.host_model, "scene_h5_host"),
            "mingyuan": self.info.get_info(self.host_model, "mingyuan_host"),
            "car_h5": self.info.get_info(self.host_model, "car_h5_host"),
            "BYD_mini": self.info.get_info(self.host_model, "car_BYD_mini_host")
        }
        publicDict.update(executeDict)
        return publicDict

    def get_host(self, product):
        '''
        获取单个host
        '''
        if publicDict == {}:
            self.get_hosts()  # 不存在则加载

        res = publicDict.get(product, None)

        if res != None:
            return res
        else:
            logger.warning(f"尚未添加此项目:{product} 的host配置，请联系自动化小组成员添加")
            raise Exception(f"project no host:{product}")

    def modify_value(self, section, option, value):
        return self.info.write_info(section, option, value)

    def middleend_browser_type(self):
        return self.info.get_info("BROWSER_TYPE", "middleend_browser_type")

    def agent_manager_browser_type(self):
        return self.info.get_info("BROWSER_TYPE", "agent_manager_browser_type")

    def pc_browser_type(self):
        return self.info.get_info("BROWSER_TYPE", "pc_browser_type")

    def get_mysql_connect(self, module):
        db_info = {}
        if self.env in (None, 'test'):
            self.mysql_module = module
            self.mysqldb = do_config.GetInfo(
                ROOT_PATH + '/config/db/' + 'test_db.cfg')
        if self.env == 'uat':
            self.mysql_module = module
            self.mysqldb = do_config.GetInfo(
                ROOT_PATH + '/config/db/' + 'uat_db.cfg')
        if self.env == 'sit2':
            self.mysql_module = module
            self.mysqldb = do_config.GetInfo(
                ROOT_PATH + '/config/db/' + 'sit2_db.cfg')

        if self.mysql_module != "":
            db_info['host'] = self.mysqldb.get_info(self.mysql_module, "host")
            db_info['port'] = self.mysqldb.get_info(self.mysql_module, "port")
            db_info['database'] = self.mysqldb.get_info(
                self.mysql_module, "database")
            db_info['user'] = self.mysqldb.get_info(self.mysql_module, "user")
            db_info['password'] = self.mysqldb.get_info(
                self.mysql_module, "password")
            return db_info
        else:
            logger.warning(
                "环境：{}，在改目录下{}无DB信息配置。请检查".format(
                    self.env, self.mysqldb))

    def get_mysql_isopen(self):
        '''
        :return: 是否开启mysql YES为启动，其他则关闭
        '''
        return self.info.get_info("DB_ISOPEN", "isOpen")


class ReadXpath:
    """
    description：获取xpath路径
    input：type：utils(公共xpath)/pc(官网)/middleend_driver(运营后台)/fcb_app_logic(房车宝APP)/
          ..
    """

    def __init__(self, type):
        if type == 'utils':
            self.ex = DoExcel(ROOT_PATH + '/data/xpath/' + 'common_xpath.xlsx')
        if type == 'pc':
            self.ex = DoExcel(ROOT_PATH + '/data/xpath/' + 'pc_xpath.xlsx')

    # 获取xpath路径
    def get_xpath(self, sheet_name, xpath_name):
        col_list = self.ex.get_column_value(sheet_name, 'name')
        index = col_list.index(xpath_name)
        cell = self.ex.get_cell_value(
            sheet_name=sheet_name, row=index + 1, column=2)
        self.ex.excel_close()
        return cell


class GetApiUrl:
    """
    description：获取接口的url地址
    """

    def __init__(self):
        self.path = ROOT_PATH + '/config/url/'

    # 获取经纪人相关接口 url
    def get_broker_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'broker_api_url.cfg')
        return url.get_info(modules, key)

    def get_customer_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'customer_api_url.cfg')
        return url.get_info(modules, key)

    # 楼盘相关接口url
    def get_prod_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'prod_api_url.cfg')
        return url.get_info(modules, key)

    # 运营后台相关接口url
    def get_om_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'om_api_url.cfg')
        return url.get_info(modules, key)

    # 中台相关接口url
    def get_middleend_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'middleend_api_url.cfg')
        return url.get_info(modules, key)

    # 会员经理接口url
    def get_bmp_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'bmp_api_url.cfg')
        return url.get_info(modules, key)

    # 机构接口url
    def get_agent_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'agent_api_url.cfg')
        return url.get_info(modules, key)

    def get_scent_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'scene_api_url.cfg')
        return url.get_info(modules, key)

    def get_car_BYD_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'car_BYD_api_url.cfg')
        return url.get_info(modules, key)


class GetApiMssg:
    """
    description：获取接口返回值中的message
    """

    def __init__(self):
        self.path = ROOT_PATH + '/config/message/'

    # 获取经纪人相关接口 返回的message
    def get_broker_api_mssg(self, modules, key):
        url = do_config.GetInfo(self.path + 'broker_api_mssg.cfg')
        return url.get_info(modules, key)

    # 楼盘相关接口 返回的message
    def get_prod_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'prod_api_mssg.cfg')
        return url.get_info(modules, key)

    # 运营中心相关接口 返回的message
    def get_om_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'om_api_mssg.cfg')
        return url.get_info(modules, key)

    # 中台相关接口 返回的message
    def get_middleend_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'middleend_api_mssg.cfg')
        return url.get_info(modules, key)

    # 机构经纪人相关接口 返回的message
    def get_agentMgr_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'agent_gr_api_mssg.cfg')
        return url.get_info(modules, key)

    # 会员经理相关接口 返回的message
    def get_member_api_url(self, modules, key):
        url = do_config.GetInfo(self.path + 'bmp_api_mssg.cfg')
        return url.get_info(modules, key)


class MyRequests:
    """
    description：封装http请求方法
    """

    def __init__(self):
        self.request = HttpRequests()

    def post(self, url, data, headers):
        return self.request.postMethod(url, data, headers)

    def get(self, url, data, headers):
        return self.request.get_method(url, data, headers)

    def session(self):
        return self.request.session()

    def session_post(self, session, url, data, headers):
        return self.request.session_post(session, url, data, headers)

    def session_get(self, session, url, data, headers):
        return self.request.session_get(session, url, data, headers)

    def get_system_cookies(self, session):
        return self.request.get_system_cookies(session)

    def http_requests(self, url, data, method, headers, product):
        return self.request.httpRequest(url, data, method, headers, product)


class ExecuteCase:
    def __init__(self, publicDict, db):
        self.publicDict = publicDict
        self.env = GetEnvInfo().get_env()
        self.proxy_host = GetEnvInfo().proxy_host
        self.privateDict = {}
        self.db = db

    def relevantParamsd(self, data: str, obj: str) -> str:
        '''
        数据进行参数替换，可替换数据包括body、headers等数据，只要在excel中加上了${}标识的数据均可从全局字典获取值替换
        :param data: 对应用例值，如body、hearders
        :param obj: 替换对象，仅用于做标识
        :return: None
        '''
        bodyRelevantParams = re.findall(r'\${([\s\S]+?)\}', data)  # 返回一个list
        if bodyRelevantParams == []:
            pass
            # logger.info(f"{obj}无依赖")
        else:
            logger.info(f"执行{obj}依赖替换")
            for relevanParams in bodyRelevantParams:
                if "." in relevanParams:  # 走多项目登录逻辑
                    params = relevanParams.split(".")
                    if params[0] in self.publicDict.keys():
                        if params[1] in self.publicDict[params[0]].keys():
                            strData = "${%s.%s}" % (params[0], params[1])
                            # 获取公共字典里面的依赖值
                            publicRelevanValue = self.publicDict[params[0]][params[1]]
                            data = data.replace(
                                strData, str(publicRelevanValue))  # 参数替换
                            logger.info(f"替换成功，{relevanParams}")
                        else:
                            logger.warning(f"替换失败，{relevanParams};请检查对应项目对应账号是否已登录成功")
                    else:
                        logger.warning(
                            f"替换失败，{relevanParams};请检查对应项目登录是否已登录成功")
                else:
                    if relevanParams in self.publicDict.keys():
                        strData = "${%s}" % relevanParams
                        # 获取公共字典里面的依赖值
                        publicRelevanValue = self.publicDict[relevanParams]
                        data = data.replace(
                            strData, str(publicRelevanValue))  # 参数替换
                        logger.info(f"替换成功，{relevanParams}")
                    else:
                        logger.warning(
                            f"替换失败，{relevanParams};失败原因：全局字典中无此key，请检查前方相关依赖接口是否有返回对应依赖")

        return data

    def relevantParams(self, data: str, obj: str) -> str:
        '''
        数据进行参数替换，可替换数据包括body、headers等数据，只要在excel中加上了${}标识的数据均可从全局字典获取值替换
        :param data: 对应用例值，如body、hearders
        :param obj: 替换对象，仅用于做标识
        :return: None
        '''
        bodyRelevantParams = re.findall(r'\${([\s\S]+?)\}', data)  # 返回一个list
        if bodyRelevantParams == []:
            pass
            # print(f"{obj}无依赖")
        else:
            logger.info(f"执行{obj}依赖替换")
            for relevanParams in bodyRelevantParams:
                if relevanParams in self.publicDict.keys():
                    strData = "${" + f"{relevanParams}" + "}"
                    if strData in data:
                        # 获取公共字典里面的依赖值
                        publicRelevanValue = self.publicDict[relevanParams]
                        if isinstance(publicRelevanValue, str):
                            data = data.replace(
                                strData, str(publicRelevanValue))  # 参数替换
                            logger.info(f"替换成功，{relevanParams}")
                        else:
                            strData_list = ['"${' + f"{relevanParams}" + '}"', "'${" + f'{relevanParams}' + "}'",
                                            "${" + f"{relevanParams}" + "}"]
                            for strData in strData_list:
                                if strData in data:
                                    data = data.replace(strData, f"{publicRelevanValue}")  # 参数替换
                                    logger.info(f"替换成功，{relevanParams}")
                                    break
                    else:
                        logger.warning(f"替换失败，无匹配的参数替换key：{relevanParams}")

                else:
                    logger.warning(
                        f"替换失败，{relevanParams};失败原因：全局字典中无此key，请检查前方相关依赖接口是否有返回对应依赖")

        return data

    def auto_data(self, autoProduct, relevantParamsFun):
        '''
        自动生成数据逻辑，并把自动生成的数据添加到全局字典
        :param autoProduct: excel用例里面的autoProduct字段的值
        :return:
        '''
        if autoProduct != "":  # 自动生成数据
            auto_product_data = RandomInfo().auto_product_data(autoProduct, relevantParamsFun)  # 引用自动生成数据方法，自动生成数据
            logger.info(f"自动生成数据：{auto_product_data}")
            for autoProductKey, autoProductValue in auto_product_data.items():
                if autoProductKey in self.publicDict.keys():
                    logger.warning(
                        f"自动生成数据时，全局字典中已存在对应key:{autoProductKey}，已执行替换操作，"
                        "请确保替换后不会对后续接口依赖处理存在影响；若影响，请更换key名称")
                # 把自动生成的数据添加到全局字典
                self.publicDict[autoProductKey] = autoProductValue
        else:
            logger.info("不需自动生成数据")

    def get_url(
            self,
            dataProduct: str,
            dataInterfacePath: str,
            body: str) -> str:
        '''
        获取请求url
        :return: url
        '''
        conf = GetEnvInfo()
        host = conf.get_host(dataProduct)
        if dataProduct != 'mingyuan':
            if 'http' in dataInterfacePath:  # 解决当接口路由已有host时，不需要再重新找host
                url = dataInterfacePath
            else:
                url = host + dataInterfacePath

        elif dataProduct == "mingyuan":
            body = eval(body)
            body["client_secret"] = self.publicDict["client_secret"]
            body["client_code"] = self.publicDict["client_code"]
            authcode = RandomInfo().get_authcode(body)  # 生成authcode
            del body["client_secret"]
            body = str(body)
            url = dataInterfacePath + f"?authcode={authcode}"
            if 'http' in dataInterfacePath:  # 解决当接口路由已有host时，不需要再重新找host
                url = url
            else:
                url = host + url

        return url, body

    def get_before_mysql(self, beforeSql):
        '''
        获取案例执行之前sql，返回值加入到公共变量中
        :retur
        '''
        if GetEnvInfo().get_mysql_isopen() == "YES":  # 增加断言是否启动逻辑 YES表示打开，NO表示关闭
            if beforeSql != "" and (self.env in ['uat'] or self.db.module_list != []):
                beforeSql = self.get_sql_data(beforeSql)  # 分割字符
                # beforeSql = eval(self.relevantParams(str(beforeSql),
                # "beforeSql"))  # 替换存在的变量
                for moudleKey, moudleValue in beforeSql.items():
                    if self.env in ['uat'] or moudleKey in self.db.module_list:
                        self.before_mysql(moudleKey, moudleValue)  # 执行模块所属脚本
                    else:
                        logger.warning(f"beforeSql列库:{moudleKey}不存在于库列表：{self.db.module_list}中，请检查！")
                        raise
            else:
                logger.info("该用例，不需执行查询sql语句")
        else:
            logger.warning("数据库开关未打开,不执行sql查询！")

    def get_except_mysql(self, exceptSql):
        '''
        获取案例执行之后sql，返回值加入到公共变量中且做断言
        :retur
        '''
        if GetEnvInfo().get_mysql_isopen() == "YES":  # 增加断言是否启动逻辑 YES表示打开，NO表示关闭
            if exceptSql != "" and (self.env in ['uat'] or self.db.module_list != []):
                exceptSql = self.get_sql_data(exceptSql)  # 分割字符
                # exceptSql = eval(self.relevantParams(str(exceptSql),
                # "exceptSql"))  # 替换存在的变量
                for moudleKey, moudleValue in exceptSql.items():
                    if moudleKey in self.db.module_list or self.env in ['uat']:
                        self.exce_mysql_more(moudleKey, exceptSql[moudleKey])
                    else:
                        logger.warning(f"exceptSql列库:{moudleKey}不存在于库列表：{self.db.module_list}中，请检查！")
                        raise
            else:
                logger.info("该用例，不需执行断言sql语句")
        else:
            logger.warning("数据库开关未打开,不执行sql查询！")

    def before_mysql(self, moudle, sql):
        # beforeSql脚本返回数据为字典，添加至公共字典
        if self.env.lower() in ['uat']:
            res_sql_dict = self.db.get_uat_fetch_resp(self.proxy_host, moudle, sql)
        else:
            res_sql_dict = self.db.get_fetch_dict(moudle, sql)  # 执行脚本生成结果
        if res_sql_dict is None:  # 判断脚本执行后是否为空
            logger.warning(f"返回值为：{res_sql_dict}，请检查SELECT脚本！INSERT、UPDATE、DELETE返回接口为None，忽略本提示。")
        else:
            for sqlDictKey, sqlDictValue in res_sql_dict.items():
                self.publicDict[sqlDictKey] = sqlDictValue  # 按原字段类型返回添加至全局字典
                logger.info(f"beforeSql添加键值对进入全局字典：{sqlDictKey}={sqlDictValue}")

    def exce_mysql_more(self, moudle, sql):
        # exceptSql脚本返回数据为字典，添加至公共字典，同时把结果保存起来已被断言。
        list_sql = []  # 初始化空list
        if self.env.lower() in ['uat']:
            res_sql_list = self.db.get_uat_fetch_resp(self.proxy_host, moudle, sql, False)
        else:
            res_sql_list = self.db.get_fetch_dict_more(moudle, sql)  # 执行脚本生成结果
        if res_sql_list is None:  # 判断脚本执行后是否为空
            logger.warning(f"返回值为：{res_sql_list}，请检查SELECT脚本！INSERT、UPDATE、DELETE返回接口为None，忽略本提示。")
        else:
            if isinstance(res_sql_list, list):
                for res_sql_dict in res_sql_list:
                    for sqlDictKey, sqlDictValue in res_sql_dict.items():
                        list_sql.append(sqlDictValue)  # 字段value转换成list
                list_sql = [str(i) for i in list_sql]  # list_sql全部转换为str
                self.privateDict[moudle] = ",".join(
                    list_sql)  # 添加以moudle为字典item，把list加到字典中去
            if isinstance(res_sql_list, dict):
                for sqlDictKey, sqlDictValue in res_sql_list.items():
                    list_sql.append(sqlDictValue)  # 字段value转换成list
                list_sql = [str(i) for i in list_sql]  # list_sql全部转换为str
                self.privateDict[moudle] = ",".join(list_sql)  # 添加以moudle为字典item，把list加到字典中去
        logger.info(f"执行断言库为：{moudle} 其执行脚本：{sql} --> 脚本返回结果{res_sql_list}")

    # def exce_mysql(self, moudleKey, sql):
    #     # exceptSql脚本返回数据为字典，添加至公共字典，同时把结果保存起来已被断言。
    #     list_sql = []  # 初始化空list
    #     res_sql_dict = self.db.get_fetch_dict(moudleKey, sql)  # 执行脚本生成结果
    #     if res_sql_dict == None:  # 判断脚本执行后是否为空
    #         logger.info("脚本返回字典值：{},请检查！".format(res_sql_dict))
    #     else:
    #         for sqlDictKey, sqlDictValue in res_sql_dict.items():
    #             self.publicDict[sqlDictKey] = sqlDictValue  # 按原字段类型返回添加至全局字典
    #             logger.info("exceptSql添加键值对进入全局字典：{}={}".format(sqlDictKey, sqlDictValue))
    #             list_sql.append(sqlDictValue)  # 字段value转换成list
    #         list_sql = [str(i) for i in list_sql]  # list_sql全部转换为str
    #         self.privateDict[moudleKey] = ",".join(list_sql)  # 添加以moudle为字典item，把list加到字典中去
    #     logger.info("执行断言库为：{} 其执行脚本：{} --> 脚本返回结果{}".format(moudleKey, sql, res_sql_dict))

    def exce_sql_assert(self, case_data):
        # 合并字典处理
        combine_dict = {}
        expectSqlResult = self.relevantParams(
            case_data["expectSqlResult"], "expectSqlResult")
        moduleResult = self.get_sql_data(expectSqlResult)  # 分割字符
        if len(moduleResult) == len(self.privateDict):
            for moduleKey in moduleResult:
                if moduleKey in self.db.module_list:
                    if combine_dict.get(moduleKey):
                        combine_dict[moduleKey].append(moduleResult[moduleKey])
                    else:
                        combine_dict[moduleKey] = [moduleResult[moduleKey]]
                else:
                    logger.warning(f"expectSqlResult列库模块:{moduleKey}不存在于库列表：{self.db.module_list}中，请检查！")
                    raise
            for privateKey in self.privateDict:
                if combine_dict.get(privateKey):
                    combine_dict[privateKey].append(
                        self.privateDict[privateKey])
                else:
                    combine_dict[privateKey] = [self.privateDict[privateKey]]
        else:
            logger.warning(
                f"expectSqlResult返回：{moduleResult}，其个数：{len(moduleResult)} 不等于 executeSql返回："
                f"{self.privateDict}，其个数：{len(self.privateDict)}, 请检查!")
            raise Exception("sql断言处理数据时，发生错误")

        return combine_dict

    # 分割处理mysql脚本数据
    def get_sql_data(self, sqlData):
        sqlDict = {}  # 定义空dict，存放最终的切割结果，为dict
        sqlData = sqlData.strip()  # 去除前后空格、换行符、双引号转换单引号等
        sqlData = sqlData.replace("\n", "")
        sqlData = sqlData.replace("\"", "'")
        # 处理字符串中有分号的特殊情况
        sqlData, tempdict = self.regular_before(sqlData)
        # 以分号分割多条sql,处理了中英文分号
        if "；" or ";" in sqlData:
            sqlList = sqlData.replace("；", ";").split(";")
            for sql in sqlList:
                if sql != "":
                    # 还原字符串数据
                    sql = self.regular_after(sql, tempdict)
                    # 以冒号分割,处理了中英文冒号,且替换一次，分割一次
                    try:
                        if ":" or "：" in sql:
                            sql = sql.replace("：", ":", 1).split(":", 1)
                            sqlDict[sql[0]] = sql[1]  # 切割为字典存入
                        # else:
                        #     logger.info("请检查该脚本是否按照规则编写！脚本：{}".format(sql))
                    except BaseException:
                        logger.warning(f"编写格式：xx:sql;xx:sql --> 编写格式说明：xx:表示数据库名称，sql表示要执行的脚本。脚本：{sql}")
                        raise Exception("excel sql编写格式错误")

                else:
                    pass  # 获取字符串以分号结尾,不执行,直接pass
        return sqlDict

    # 正则提取值
    def regular_before(self, data):
        templist = []  # 临时list，防止sql脚本中有分号被错误分割
        res = re.findall(r"['](.*?)[']", data)  # 正则提取双引号中的sql脚本数据
        for num in range(len(res)):
            templist.append('temp_%s' % str(num))  # 定义双引号中的临时变量
        # 临时变量：正则提取双引号中值 合并成tempdict字典
        datadict = dict(map(lambda tempKey, tempValue: [tempKey, tempValue], templist, res))
        # 使用临时变量替换掉sql脚本引号中的值
        for tempKey, tempValue in datadict.items():
            if tempValue in data:
                data = data.replace(tempValue, tempKey)
        return data, datadict

    # 还原sql中引号里面的值
    def regular_after(self, data, datadict):
        for tempKey, tempValue in datadict.items():
            if tempKey in data:
                data = data.replace(tempKey, tempValue)
        return data

    def wait_time(self, case_data):
        if "wait" in case_data.keys():
            wait = case_data["wait"]
            if wait == "":
                pass
            else:
                try:
                    logger.info(f"已设置等待时间：{wait}s，请耐心等待！")
                    time.sleep(wait)
                except BaseException:
                    logger.error("excel的wait填写格式错误，填写仅支持数字int")

    def http_request_count(self, method, url, headers, data, case_data, product):
        '''
        再次封装http_requests,根据用例里面的count字段数值，循环请求
        :return: 响应结果
        '''
        if "count" in case_data.keys():
            count = case_data["count"]
            if count in ("", 1):
                response = MyRequests().http_requests(url, data, method, headers, product)
            else:
                for c in range(2, count + 1):
                    logger.info(f"该用例总计需发起{count}次请求，现发起第{c}次请求...")
                    response = MyRequests().http_requests(url, data, method, headers, product)
                    if response[0] == 200:
                        logger.info("请求成功！")
                    else:
                        logger.warning(f"请求失败，http响应码:{response[0]}，response:{response[1]}")
        else:
            response = MyRequests().http_requests(url, data, method, headers, product)

        return response

    # @Decorators.add_log
    def exec_request(self, case_data):
        '''
        对请求的body、headers做处理，并发起请求
        param case_data: 测试用例数据
        :param
        :return: None
        '''
        logger.debug(f"全局字典：{self.publicDict}")
        # logger.debug(f"用例文件：{case_data['excelPath']}")
        # logger.debug(f"用例sheet：{case_data['excelSheet']}")
        # logger.info(f"模块：{case_data['module']}")
        # logger.info(f"用例级别：{case_data['priority']}")
        logger.info(f"用例描述：{case_data['description']}")
        logger.info(f"请求接口:{case_data['interfaceName']}")
        logger.info(f"请求方式:{case_data['method']}")

        relevantParamsFun = self.relevantParams  # 获取参数替换引用对象，提供给下方autoProduct进行参数替换
        self.auto_data(case_data["autoProduct"], relevantParamsFun)  # 进入自动生成数据逻辑，包含参数替换逻辑
        # 参数替换模块
        self.beforeSql = self.relevantParams(case_data["beforeSql"], "beforeSql")  # 进行beforeSql的参数替换
        # 执行sql模块,sql执行会产生公共变量给当前案例使用，所以执行在header和body之前更合理
        self.get_before_mysql(self.beforeSql)
        interfacePath = self.relevantParams(case_data["interfacePath"], "interfacePath")  # 进行interfacePath的关联参数替换
        body = self.relevantParams(case_data["body"], "body")  # 进行body的关联参数替换
        headers = self.relevantParams(case_data["headers"], "headers")  # 进行headers的关联参数替换
        self.assertResult = self.relevantParams(case_data["assert"], "assert")  # 进行assertResult的关联参数替换
        self.executeSql = self.relevantParams(case_data["executeSql"], "executeSql")  # 进行exceptSql的关联参数替换
        self.relevantParams(case_data["expectSqlResult"], "expectSqlResult")  # 进行expectSqlResult的关联参数替换

        null = None
        false = False
        true = True  # 容错处理，兼容请求body中存在的特殊变量
        url, body = self.get_url(case_data["product"], interfacePath, body)
        logger.info(f"请求路由interfacePath：{interfacePath}")
        logger.info(f"请求url：{url}")
        logger.info(f"请求头headers：{eval(headers)}")
        logger.info(f"请求参数：{eval(body)}")
        # 发起请求
        self.response = self.http_request_count(
            method=case_data["method"],
            url=url,
            headers=eval(headers),
            data=eval(body),
            case_data=case_data,
            product=case_data["product"])

        self.wait_time(case_data)  # 设置等待时间
        logger.info(f"http响应码：{self.response[0]}")
        logger.info(f"响应结果：{self.response[1]}")

        # 执行查询断言
        self.get_except_mysql(self.executeSql)
        return self.response

    # 根据jsonpath把接口依赖数据添加到全局字典里面
    def exec_save_data(self, case_data):
        # 根据定位表达式，从response里面拿到对应的值，并添加到全局字典中
        result = DataProcess().split_for_save(case_data["save"])  # 返回一个嵌套字典
        # for globalKey, globalValue in case_data["globalData"].items():
        for saveValue in result:
            resGlobalValue = jsonpath.jsonpath(self.response[1], saveValue["jsonPath"])
            logger.debug(f"json提取值为：{resGlobalValue}")
            if resGlobalValue:
                # 如果返回只有一个值时,获取定位表达式结果list里面的第一个值,如果返回多个值时，直接返回一个list
                if saveValue['key'] in self.publicDict.keys():  # 判断当前声明全局变量的key是否在全局字典内
                    logger.warning(
                        f"save时，全局字典中已存在依赖key:{saveValue['key']}的值，下面会执行替换操作，"
                        "请确保替换后不会对后续接口依赖处理存在影响；若影响，请更换依赖key名称")
                if len(resGlobalValue) == 1:  # 只有一个值，则提取出来
                    self.publicDict[saveValue['key']] = resGlobalValue[0]
                    logger.info(f"成功save依赖：{saveValue['key']}={resGlobalValue[0]}，默认提取位置：1")
                else:
                    if "index" in saveValue.keys():
                        if saveValue["index"] == 0:
                            index = random.randint(1, len(resGlobalValue))
                            self.publicDict[saveValue['key']] = resGlobalValue[index - 1]
                            logger.info(f"成功save依赖：{saveValue['key']}={resGlobalValue[index - 1]}，随机提取位置：{index}")
                        elif isinstance(saveValue['index'], int):
                            if saveValue["index"] > len(resGlobalValue):
                                logger.warning(f"save依赖异常，{saveValue['key']}无此位置：{saveValue['index']} 的匹配值，"
                                               f"将默认取第一个值")
                                self.publicDict[saveValue['key']] = resGlobalValue[0]
                                logger.info(f"成功save依赖：{saveValue['key']}={resGlobalValue[0]}，默认提取位置：1")
                            else:
                                self.publicDict[saveValue['key']] = resGlobalValue[saveValue["index"] - 1]
                                logger.info(f"成功save依赖：{saveValue['key']}={resGlobalValue[saveValue['index'] - 1]}，"
                                            f"提取位置：{saveValue['index']}")

                        elif isinstance(saveValue['index'], str):
                            try:
                                res = eval(''.join((f"{resGlobalValue}", saveValue['index'])))
                                self.publicDict[saveValue['key']] = res
                                logger.info(f"成功save依赖：{saveValue['key']}={res}，"
                                            f"提取位置：{saveValue['index']}")
                            except:
                                logger.warning("再次提取表达式填写有误，请正确填写！")



                    else:
                        self.publicDict[saveValue['key']] = resGlobalValue
                        logger.info(f"成功save依赖：{saveValue['key']}={resGlobalValue}，提取位置：None")
            else:
                logger.warning("无法获取到jsonpath定位结果，请确认response是否有返回，或检查定位表达式")

        # logger.debug(f"save依赖后全局字典为：{self.publicDict}")

    # def get_assert_result(self):
    #     '''
    #     获取表格里面的数据，把断言需要的数据放在一个list里面，最后组成一个嵌套list
    #     :param case_data:  用例数据
    #     :return: result
    #     '''
    #     dictObj = {}
    #     splitData = DataProcess().split_for_assert(self.assertResult)
    #     if splitData != {}:
    #         for key, value in splitData.items():
    #             dictObj[key] = []
    #             for listObj in value:
    #                 assertList = []  # 每次初始化
    #                 if key in ("||"):
    #                     for orValue in listObj:
    #                         orDict = {}
    #                         orList = []
    #                         for k, v in orValue.items():
    #                             response_filter_or = jsonpath.jsonpath(
    #                                 self.response[1], v[1])
    #                             if response_filter_or:
    #                                 exceptResult = v[0]
    #                                 orList.append(exceptResult)
    #                                 if len(response_filter_or)==1:
    #                                     orList.append(response_filter_or[0])  #如果返回一个值，则提取
    #                                 else:
    #                                     orList.append(response_filter_or)  #若返回多个值，则返回数组
    #                                 orDict[k] = copy.deepcopy(orList)
    #                                 assertList.append(copy.deepcopy(orDict))
    #                             else:
    #                                 logger.warning(
    #                                     f"断言对象json提取值失败({v[1]}={response_filter_or})，请检查response是否有对应字段返回，"
    #                                     "或json定位表达式是否正确")
    #                                 raise Exception("断言时，json提取值异常")
    #                     dictObj[key].append(copy.deepcopy(assertList))
    #                 else:
    #                     response_filter = jsonpath.jsonpath(
    #                         self.response[1], listObj[1])  # response的过滤结果
    #                     exceptResult = listObj[0]  # 预期结果
    #                     if response_filter:
    #                         assertList.append(exceptResult)
    #                         if len(response_filter)==1:
    #                             assertList.append(response_filter[0])  # 若返回一个值，则提取
    #                         else:
    #                             assertList.append(response_filter)  #若返回多个值，则返回数组
    #                         dictObj[key].append(copy.deepcopy(assertList))
    #                     else:
    #                         logger.warning(
    #                             f"断言对象json提取值失败({listObj[1]}={response_filter})，请检查response是否有对应字段返回，"
    #                             "或json定位表达式是否正确")
    #                         raise Exception("断言时，json提取值异常")
    #     else:
    #         pass
    #
    #     return dictObj

    def get_assert_result(self):
        '''
        获取表格里面的数据，把断言需要的数据放在一个list里面，最后组成一个嵌套list
        :param case_data:  用例数据
        :return: result
        '''
        dictObj = {}
        splitData = DataProcess().split_for_assert(self.assertResult)
        if splitData != {}:
            for key, value in splitData.items():
                dictObj[key] = []
                for obj in value:
                    assertList = []  # 每次初始化
                    if key in ("||"):
                        for orValue in obj:
                            orDict = {}
                            orList = []
                            for k, v in orValue.items():
                                response_filter_or = jsonpath.jsonpath(self.response[1], v["jsonPath"])
                                if response_filter_or:
                                    exceptResult = v["expectRes"]
                                    orList.append(exceptResult)
                                    if len(response_filter_or) == 1:
                                        orList.append(response_filter_or[0])  # 如果返回一个值，则提取
                                    else:
                                        if "index" in v.keys():
                                            if isinstance(obj["index"], int):
                                                if v["index"] == 0:
                                                    index = random.randint(1, len(response_filter_or))
                                                    orList.append(response_filter_or[index - 1])
                                                elif v["index"] > len(response_filter_or):
                                                    logger.warning(
                                                        f"json提取值二次提取异常，value={response_filter_or},无此位置："
                                                        f"{v['index']}的匹配值，将默认使用第一个值")
                                                    orList.append(response_filter_or[0])  # 默认提取jsonPath的第一个值
                                                else:
                                                    orList.append(response_filter_or[v["index"] - 1])  # 提取jsonPath数组的值

                                            elif isinstance(obj["index"], str):
                                                res = eval(''.join((f"{response_filter_or}", obj['index'])))
                                                self.publicDict[obj['key']] = res
                                        else:
                                            orList.append(response_filter_or)  # 若返回多个值，且不需要提取，则返回数组
                                    orDict[k] = copy.deepcopy(orList)
                                    assertList.append(copy.deepcopy(orDict))
                                else:
                                    logger.warning(
                                        f"断言对象json提取值失败({v['jsonPath']}={response_filter_or})，请检查response是否有对应字段返回，"
                                        "或json定位表达式是否正确")
                                    raise Exception("断言时，json提取值异常")
                        dictObj[key].append(copy.deepcopy(assertList))
                    else:
                        response_filter = jsonpath.jsonpath(self.response[1], obj["jsonPath"])  # response的过滤结果
                        exceptResult = obj["expectRes"]  # 预期结果
                        if response_filter:
                            assertList.append(exceptResult)
                            if len(response_filter) == 1:
                                assertList.append(response_filter[0])  # 若返回一个值，则提取
                            else:
                                if "index" in obj.keys():
                                    if isinstance(obj["index"], int):
                                        if obj["index"] == 0:
                                            index = random.randint(1, len(response_filter))
                                            assertList.append(response_filter[index - 1])
                                        elif obj["index"] > len(response_filter):
                                            logger.warning(f"json提取值二次提取异常，value={response_filter},"
                                                           f"无此位置：{obj['index']}的匹配值，将默认使用第一个值")
                                            assertList.append(response_filter[0])  # 默认提取jsonPath的第一个值
                                        else:
                                            assertList.append(response_filter[obj["index"] - 1])  # 提取jsonPath数组的值

                                    elif isinstance(obj["index"], str):
                                        res = eval(''.join((f"{response_filter}", obj['index'])))
                                        assertList.append(res)
                                else:
                                    assertList.append(response_filter)  # 若返回多个值，且不需要提取，则返回数组
                            dictObj[key].append(copy.deepcopy(assertList))
                        else:
                            logger.warning(
                                f"断言对象json提取值失败({obj['expectRes']}={response_filter})，请检查response是否有对应字段返回，"
                                "或json定位表达式是否正确")
                            raise Exception("断言时，json提取值异常")
        else:
            pass

        return dictObj


if __name__ == '__main__':
    print(UserInfo().get_app_broker_login_account())
