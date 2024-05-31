import time
import os
from interface_runner.data_driver.common.base import RandomInfo
from interface_runner.data_driver.common.do_config import GetInfo
from interface_runner.data_driver.common.project_path import *

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# 设置全局字典
publicDictForFcbBrokerApp = {}
publicDictForFcbCustomerApp = {}
publicDictForAgentMgrPlatform = {}
publicDictForBmpMgrPlatfrom = {}
publicDictForFcbMgrPlatform = {}
publicDictForSceneBaoApp = {}
publicDictForCarBYDMini = {}


class GetCaseInfo():
    '''
    获取用例相关信息的类，包括运行用户，运行数据库，运行环境url等
    '''

    def __init__(self):
        self.info = GetInfo(ROOT_PATH + '/config/' + 'env_info.cfg')
        self.env = self.info.get_info('ENV', 'env')
        if self.env in (None, 'test'):
            self.public_info_path = public_info_path_sit
        elif self.env == 'uat':
            self.public_info_path = public_info_path_uat
        elif self.env == 'sit2':
            self.public_info_path = public_info_path_sit2

    def get_public_conf_case_info(self, project, public="public"):
        publicDict = {}
        confPublic = GetInfo(self.public_info_path).get_info_for_public(
            public)  # 获取公共配置文件形成的字典
        confDict = GetInfo(self.public_info_path).get_info_for_public(project)
        publicDict.update(confPublic)  # 添加配置文件的公共键值对进入全局字典
        publicDict.update(confDict)  # 添加配置文件的对应项目键值对进入全局字典

        return publicDict

    def public_all(self):
        '''
        公共字典，提供给其他项目使用
        :return:
        '''
        publicDict = {}
        publicDict["now_time"] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime())
        publicDict["now_date"] = RandomInfo().get_date(0, tag="+")
        publicDict["end_date"] = RandomInfo().get_date(60, tag="+")
        publicDict["timestamp"] = str(round(time.time() * 1000))  # 13位毫秒级时间戳
        publicDict["timestamp_sec"] = str(round(time.time()))  # 10位秒级时间戳
        publicDict["start_time"] = RandomInfo().get_time(
            30, tag="-")  # 当前时间减去30天
        publicDict["end_time"] = RandomInfo().get_time(
            30, tag="+")  # 当前时间加去30天
        publicDict["now_date2"] = time.strftime("%m%d", time.localtime())
        publicDict["now_date1"] = time.strftime("%Y-%m-%d", time.localtime())

        return publicDict

    def public_for_fcb_broker_app(self, publicDict, caseInfoConf, tag=[]):
        '''
        把需要的数据添加进入broker项目的全局字典，供运行测试用例使用
        '''

        publicDictForFcbBrokerApp.update(publicDict)  # 把登录信息加入全局字典
        publicDictForFcbBrokerApp.update(self.public_all())  # 把即时生成的时间等信息加入字典
        publicDictForFcbBrokerApp.update(caseInfoConf)  # 加载配置文件用例信息

        # 获取timestamp
        publicDict["timestamp"] = publicDictForFcbBrokerApp["timestamp"]
        signDict = RandomInfo().get_sign_tag(publicDict, "fcb_broker_app", tag)  # 获取SIGN加密
        publicDictForFcbBrokerApp.update(signDict)  # 把生成的sig添加进入全局字典

        return publicDictForFcbBrokerApp

    def public_for_fcb_customer_app(self, publicDict, caseInfoConf, tag=[]):
        '''
        把需要的数据添加进入customer项目的全局字典，供运行测试用例使用
        '''
        publicDictForFcbCustomerApp.update(publicDict)  # 把登录信息加入全局字典
        publicDictForFcbCustomerApp.update(
            self.public_all())  # 把即时生成的时间等信息加入字典
        publicDictForFcbCustomerApp.update(caseInfoConf)

        # 获取timestamp
        publicDict["timestamp"] = publicDictForFcbCustomerApp["timestamp"]
        signDict = RandomInfo().get_sign_tag(publicDict, "fcb_customer_app", tag)  # 获取SIGN加密
        publicDictForFcbCustomerApp.update(signDict)  # 把生成的sig添加进入全局字典

        return publicDictForFcbCustomerApp

    def public_for_agent_mgr_platform(self, publicDict, caseInfoConf, tag=[]):
        '''
        把需要的数据添加进入agent_mgr的全局字典，供运行测试用例使用
        '''

        publicDictForAgentMgrPlatform.update(publicDict)  # 把登录信息加入全局字典
        publicDictForAgentMgrPlatform.update(
            self.public_all())  # 把即时生成的时间等信息加入字典
        publicDictForAgentMgrPlatform.update(caseInfoConf)

        publicDict["timestamp"] = publicDictForAgentMgrPlatform["timestamp"]
        signDict = RandomInfo().get_sign_tag(publicDict, "agent_mgr_platform", tag)  # 获取SIGN加密
        publicDictForAgentMgrPlatform.update(signDict)  # 把生成的sig添加进入全局字典

        return publicDictForAgentMgrPlatform

    def public_for_bmp_mgr_platfrom(self, publicDict, caseInfoConf, tag=[]):
        '''
        把需要的数据添加进入全局字典，供运行测试用例使用
        '''

        publicDictForBmpMgrPlatfrom.update(publicDict)  # 把登录信息加入全局字典
        publicDictForBmpMgrPlatfrom.update(
            self.public_all())  # 把即时生成的时间等信息加入字典
        publicDictForBmpMgrPlatfrom.update(caseInfoConf)

        publicDict["timestamp"] = publicDictForBmpMgrPlatfrom["timestamp"]
        signDict = RandomInfo().get_sign_tag(publicDict, "bmp_mgr_platfrom", tag)  # 获取SIGN加密
        publicDictForBmpMgrPlatfrom.update(signDict)  # 把生成的sig添加进入全局字典

        return publicDictForBmpMgrPlatfrom

    def public_for_fcb_mgr_platform(self, publicDict, caseInfoConf, tag=[]):
        '''
        把需要的数据添加进入fcb_mgr的全局字典，供运行测试用例使用
        '''
        publicDictForFcbMgrPlatform.update(publicDict)  # 把登录信息加入全局字典
        publicDictForFcbMgrPlatform.update(
            self.public_all())  # 把即时生成的时间等信息加入字典
        publicDictForFcbMgrPlatform.update(caseInfoConf)

        # 获取timestamp
        publicDict["timestamp"] = publicDictForFcbMgrPlatform["timestamp"]
        signDict = RandomInfo().get_sign_tag(publicDict, "fcb_mgr_platform", tag)  # 获取SIGN加密
        publicDictForFcbMgrPlatform.update(signDict)  # 把生成的sig添加进入全局字典

        return publicDictForFcbMgrPlatform

    def public_for_scene_bao_app(self, publicDict, caseInfoConf, tag=[]):
        '''
        把需要的数据添加进入scene的全局字典，供运行测试用例使用
        '''
        publicDictForSceneBaoApp.update(publicDict)  # 把登录信息加入全局字典
        publicDictForSceneBaoApp.update(self.public_all())  # 把即时生成的时间等信息加入字典
        publicDictForSceneBaoApp.update(caseInfoConf)

        # 获取timestamp
        publicDict["timestamp"] = publicDictForSceneBaoApp["timestamp"]
        signDict = RandomInfo().get_sign_tag(publicDict, "scene_bao_app", tag)  # 获取SIGN加密
        publicDictForSceneBaoApp.update(signDict)  # 把生成的sig添加进入全局字典

        return publicDictForSceneBaoApp

    def public_for_car_BYD_mini(self, publicDict, caseInfoConf, tag=[]):
        '''
        把需要的数据添加进入scene的全局字典，供运行测试用例使用
        '''
        publicDictForCarBYDMini.update(publicDict)  # 把登录信息加入全局字典
        publicDictForCarBYDMini.update(self.public_all())  # 把即时生成的时间等信息加入字典
        publicDictForCarBYDMini.update(caseInfoConf)

        # 获取timestamp
        publicDict["timestamp"] = publicDictForCarBYDMini["timestamp"]
        # signDict = RandomInfo().get_sign_tag(publicDict, "scene_bao_app",tag)  # 获取SIGN加密
        # publicDictForCarBYDMini.update(signDict)  # 把生成的sig添加进入全局字典

        return publicDictForCarBYDMini

    def public_info(self, publicDict, caseInfoConf, public_dict, project_tag, tag=[]):
        '''
        把需要的数据添加进入customer项目的全局字典，供运行测试用例使用
        '''
        public_dict.update(publicDict)  # 把登录信息加入全局字典
        public_dict.update(
            self.public_all())  # 把即时生成的时间等信息加入字典
        public_dict.update(caseInfoConf)

        # 获取timestamp
        publicDict["timestamp"] = public_dict["timestamp"]
        signDict = RandomInfo().get_sign_tag(publicDict, project_tag, tag)  # 获取SIGN加密
        public_dict.update(signDict)  # 把生成的sig添加进入全局字典

        return public_dict


if __name__ == "__main__":
    s = GetCaseInfo().public_for_fcb_broker_app({})
    print(s)
