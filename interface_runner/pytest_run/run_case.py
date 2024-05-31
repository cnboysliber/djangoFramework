# coding:utf-8
import allure
import os
from interface_runner.data_driver.common.data_process import DataProcess
from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.common.base import ExecuteCase as exec_case, GetEnvInfo
# from interface_runner.pytest_run.conftest import get_login

dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
logger = GetLog().logger()  # 引入日志模块


class RunTest:

    def __init__(self, case_data,sign, loginStr, db_loginFun, publicDictFun, caseInfoConf,public_dict,project_tag):
        #self.case_data, self.project = DataProcess().get_case_project_data(case_data)
        self.case_data=case_data
        self.project=None
        ss=self.case_data["loginTag"]  #['bro']
        #self.login_info = get_login(loginStr, self.case_data["loginTag"])
        self.login_info = loginStr
        self.login_info['sign']=sign  #赋值sgin
        self.login_info[self.case_data["loginTag"][0]]={}  #临时给tag添加一个空登录态字典，后需删除
        self.publicDict = publicDictFun(self.login_info, caseInfoConf,public_dict,project_tag, self.case_data["loginTag"])  # 把其他需要的数据添加到全局字典
        self.db = db_loginFun
        self.ec = exec_case(self.publicDict, self.db)  # 运行用例类初始化

    def runCase(self):
        case_data, project = self.case_data, self.project  # 获取项目目录以及测试用例数据
        allure.dynamic.story(project)
        allure.dynamic.title("{}::{}".format(case_data["interfacePath"], case_data["interfaceName"]))
        allure.dynamic.description("接口描述:{} :: {}".format(case_data["interfacePath"], case_data["description"]))
        priority = case_data["priority"]
        if priority == 'P0':
            allure.dynamic.severity("critical")
        elif priority == 'P1':
            allure.dynamic.severity("major")
        else:
            allure.dynamic.severity("minor")

        logger.info("***** STEP 1 *****:数据准备，发送request请求")
        # ec.exec_request(case_data=case_data, env=self.env)
        self.ec.exec_request(case_data)

        logger.info("***** STEP 2 *****:查看该用例是否被其他接口依赖")
        if case_data["save"] != "":
            self.ec.exec_save_data(case_data=case_data)
        else:
            logger.info("save，其他接口不依赖当前接口")

        logger.info("***** STEP 3 *****:执行断言")
        if case_data["assert"] != "":
            logger.info("*****：进入response断言")
            try:
                self.get_response_assert()
                logger.info("断言通过->all")
            except Exception as error:
                logger.warning("执行失败->响应断言")
                raise error

            finally:  # 无论response断言是否通过，均进行数据库校验断言
                logger.info("*****：进入sql断言")
                try:
                    self.get_sql_assert(case_data)
                except Exception as error:
                    logger.warning("执行失败->sql断言")
                    raise error

            logger.info("执行通过")
            logger.debug("当前全局字典：{}".format(self.publicDict))

    def get_response_assert(self):
        result = self.ec.get_assert_result()  # 返回字典，字典的每个value是嵌套list
        for assertKey, assertValue in result.items():
            for assertResult in assertValue:
                if assertKey in ("||"):
                    for k0, v0 in assertResult[0].items():
                        for k1, v1 in assertResult[1].items():
                            logger.info(
                                "断言类型：%s << %r %s %r %s %r %s %r >>" % (
                                assertKey, v0[0], k0, v0[1], assertKey, v1[0], k1, v1[1]))
                            if k0 == "=":
                                if k1 == "=":
                                    assert v0[0] == v0[1] or v1[0] == v1[1]
                                elif k1 == "in":
                                    assert v0[0] == v0[1] or str(v1[0]) in str(v1[1])
                                elif k1 == "!=":
                                    assert v0[0] == v0[1] or v1[0] != v1[1]
                                elif k1 == "not in":
                                    assert v0[0] == v0[1] or str(v1[0]) not in str(v1[1])
                            elif k0 == "in":
                                if k1 == "=":
                                    assert str(v0[0]) in str(v0[1]) or v1[0] == v1[1]
                                elif k1 == "in":
                                    assert str(v0[0]) in str(v0[1]) or str(v1[0]) in str(v1[1])
                                elif k1 == "!=":
                                    assert str(v0[0]) in str(v0[1]) or v1[0] != v1[1]
                                elif k1 == "not in":
                                    assert str(v0[0]) in str(v0[1]) or str(v1[0]) not in str(v1[1])
                            elif k0 == "!=":
                                if k1 == "=":
                                    assert v0[0] != v0[1] or v1[0] == v1[1]
                                elif k1 == "in":
                                    assert v0[0] != v0[1] or str(v1[0]) in str(v1[1])
                                elif k1 == "!=":
                                    assert v0[0] != v0[1] or v1[0] != v1[1]
                                elif k1 == "not in":
                                    assert v0[0] != v0[1] or str(v1[0]) not in str(v1[1])
                            elif k0 == "not in":
                                if k1 == "=":
                                    assert str(v0[0]) not in str(v0[1]) or v1[0] == v1[1]
                                elif k1 == "in":
                                    assert str(v0[0]) not in str(v0[1]) or str(v1[0]) in str(v1[1])
                                elif k1 == "!=":
                                    assert str(v0[0]) not in str(v0[1]) or v1[0] != v1[1]
                                elif k1 == "not in":
                                    assert str(v0[0]) not in str(v0[1]) or str(v1[0]) not in str(v1[1])

                else:
                    logger.info("断言类型：%s << %r %s %r >>" % (assertKey, assertResult[0], assertKey, assertResult[1]))
                    if assertKey == "=":
                        assert assertResult[0] == assertResult[1]
                    elif assertKey == "in":
                        assert str(assertResult[0]) in str(assertResult[1])
                    elif assertKey == "!=":
                        assert assertResult[0] != assertResult[1]
                    elif assertKey == "not in":
                        assert str(assertResult[0]) not in str(assertResult[1])

    def get_sql_assert(self, case_data):
        if GetEnvInfo().get_mysql_isopen() == "YES":
            if case_data["executeSql"] != "" and self.db.module_list != []:
                if case_data["expectSqlResult"] != "":
                    assert_dict = self.ec.exce_sql_assert(case_data)
                    for assertKey, assertValue in assert_dict.items():
                        if "," or "，" in assert_dict[assertKey][0]:
                            moduleRes = tuple(assert_dict[assertKey][0].split(","))
                        else:
                            moduleRes = tuple(assert_dict[assertKey][0])
                        for pv in moduleRes:
                            logger.info("库%s：断言类型：in << %r in %r >>" % (assertKey, pv, assert_dict[assertKey][1]))
                            assert pv in assert_dict[assertKey][1]

                    logger.info("断言通过->all")
                else:
                    for privateKey, privateVaule in self.ec.privateDict.items():
                        # list_pv = []
                        # 分割后单个断言于接口返回的结果
                        if "," or "，" in privateVaule:
                            privateVaule = tuple(privateVaule.split(","))
                        else:
                            privateVaule = tuple(privateVaule)
                        for pv in privateVaule:
                            logger.info("库%s：断言类型：in << %r in %r >>" % (privateKey, pv, self.ec.response))
                            assert pv in self.ec.response

                    logger.info("断言通过->all")
            else:
                logger.info("不需进行数据库校验或数据库异常")
        else:
            logger.info("数据库开关未打开，不执行断言")


if __name__ == "__main__":
    pass
