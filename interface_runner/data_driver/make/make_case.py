import jinja2
import os
import re
import time
import platform
from FasterRunner.settings.pro import INTERFACE_REPORT_PATH_PRO, INTERFACE_SUITE_PATH_PRO
from FasterRunner.settings.dev import INTERFACE_REPORT_PATH_DEV, INTERFACE_SUITE_PATH_DEV
from .gather_result import gather_str
from interface_runner import models
from interface_runner.utils.prepare import get_random_num
from FasterRunner.utils.projectPath import path_project

pytest_run_str = jinja2.Template('''
# coding:utf-8
import pytest
import allure
import os
from interface_runner.pytest_run.run_case import RunTest
from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.common.data_process import GetCaseData as get_case
from interface_runner.data_driver.common.get_case_info import GetCaseInfo

dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
logger = GetLog().logger()  # 引入日志模块
#caseInfoConf = GetCaseInfo().get_public_conf_case_info('{{project_tag}}')
public_dict={}  #全局字典

@allure.epic('{{epic}}')
@allure.feature('{{project_name}}')
@pytest.mark.parametrize('case_data', {{case_data_all}})
class TestInterface():
    def setup_class(self):
        logger.info("-" * 20 + "BEGIN:{{project_name}}接口测试" + "-" * 20)

    #@pytest.mark.skipif(resultExcelFile == {}, reason="resultExcelFile is empty")
    def test_scene_bao_api(self,case_data,fcb_get_db_login,{{login_fun_str}},sign):
        RunTest(case_data,sign,{{login_fun_str}},fcb_get_db_login,GetCaseInfo().public_info,{{config_data}},public_dict,'{{project_tag}}').runCase()

    def teardown_class(self):
        logger.info("-" * 20 + "END：{{project_name}}接口测试" + "-" * 20)


if __name__ == "__main__":
    pytest.main(["-s", r"{{test_file_path}}"])
'''
                                 )

db_login_str = """
import pytest
from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.common.do_mysql import ExceteMysql
from interface_runner.data_driver.common.base import GetEnvInfo
logger=GetLog().logger()

@pytest.fixture(scope='session')
def fcb_get_db_login():
    '''
        数据库登录
        :return: 登录信息
    '''
    # 初始化所有数据库打开
    all_accounts = {{db_config}}
    env='{{env}}'.lower()
    if GetEnvInfo().get_mysql_isopen() == "YES":  # 增加断言是否启动逻辑 YES表示打开，NO表示关闭
        if env not in ['uat'] and all_accounts == {}:
            logger.warning(f"数据库配置数据为空{all_accounts}，若需查库，请配置！")
        else:
            if env not in ("uat"):
                logger.info(f"数据库配置信息：{all_accounts}")
            login_res = ExceteMysql(env,all_accounts)
            return login_res
    else:
        logger.warning("-" * 10 + "数据库开关未打开！" + "-" * 10)
        
"""


class MakeCase:
    def __init__(self, user, id):
        self.id = id
        self.base_path = None
        self.suit_work_dir = None
        self.user = user
        self.gather_tag=False  #收集测试结果数据的一个tag，用于标识

    def get_fun_name(self, data: str):
        '''
        获取login的str里面的函数名称
        :param data: login str
        :return: fun name
        '''
        res_list = re.findall(r"(?<=def).*(?=:)", data)
        fun_str = res_list[0].strip().replace('()', '')  # 默认获取第一个函数名称做为登录函数名
        return fun_str

    def gen_report_dir(self,report_name):
        now_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        six_num = get_random_num(6)
        self.time_num = "".join((now_time, "_", six_num))
        if platform.system().lower() == "windows":
            user_report_dir = os.path.join(INTERFACE_REPORT_PATH_DEV, f"{self.user}_workDir")
            self.report_work_dir = os.path.join(user_report_dir, f"{report_name}_reportDir")
        else:
            self.report_work_dir = os.path.join(INTERFACE_REPORT_PATH_PRO, f"{self.user}_workDir",
                                                f"{report_name}_reportDir")
        if os.path.exists(self.report_work_dir):
            pass
        else:
            os.makedirs(self.report_work_dir)

        self.allure_results_dir = os.path.join(self.report_work_dir, 'allure-results')
        self.allure_report_dir = os.path.join(self.report_work_dir, 'allure-report')
        self.allure_report_command = f'allure generate {self.allure_results_dir} -o {self.allure_report_dir} --clean'

    def gen_suit_work_dir(self):
        now_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        six_num = get_random_num(6)
        self.user_time_num = "".join((self.user,"_",now_time, "_", six_num))  # 生成测试报告名称使用
        if platform.system().lower() == "windows":
            # self.suit_work_dir = os.path.join(INTERFACE_SUITE_PATH_DEV, f"{self.user}_suitesDir",
            #                                   f"{now_time}_{six_num}_suiteWorkDir")
            self.suit_work_dir = os.path.join(INTERFACE_SUITE_PATH_DEV,
                                              f"{self.user}_{now_time}_{six_num}_suiteWorkDir")
        else:
            # self.suit_work_dir = os.path.join(INTERFACE_SUITE_PATH_PRO, f"{self.user}_suitesDir",
            #                                   f"{now_time}_{six_num}_suiteWorkDir")
            self.suit_work_dir = os.path.join(INTERFACE_SUITE_PATH_PRO,
                                              f"{self.user}_{now_time}_{six_num}_suiteWorkDir")
        if os.path.exists(self.suit_work_dir):
            pass
        else:
            os.makedirs(self.suit_work_dir)

    def gen_work_dir(self):
        if self.suit_work_dir:
            # now_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            self.num = get_random_num(6)
            work_path = os.path.join(self.suit_work_dir, f"runTestDir{self.num}")
            if os.path.exists(work_path):
                self.base_path = work_path
                pass
            else:
                os.makedirs(work_path)
                self.base_path = work_path

    def gen_pytest_file_path(self) -> str:
        if not self.base_path:
            self.gen_work_dir()
        path = os.path.join(self.base_path, f"{self.num}_test.py")
        return path

    def gen_conftest_file_path(self) -> str:
        if not self.base_path:
            self.gen_work_dir()
        path = os.path.join(self.base_path, "conftest.py")
        return path

    def write_pytest_file(self, test_file_path: str, data: str) -> None:
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(data)

    def make_conftest_file(self, conftest_file_path: str, config_data: dict, project_name: str, report_name: str,
                           code: str, run_type: int, user: str) -> None:

        env_id = models.Env.objects.get(name=config_data["env"]).id

        gather_res_data = {
            'project_name': project_name,
            'report_name': report_name,
            'report_type': run_type,
            'env_id': env_id,
            'user': user,
        }
        if 'config' in config_data.keys() and 'ac_config' in config_data.keys():
            login_data = {
                'url': config_data['config']['request']['base_url'],
                'login': config_data['ac_config']['ac_info'],
                'db_config': config_data['db_config'],
                'env': config_data['env'],
            }

        self.login_fun = self.get_fun_name(code)
        if not self.gather_tag:  #若已在第一个conftest里面加入收集测试数据的gather_str，则不再添加
            conftest_str = "".join((db_login_str, '\n', code, '\n', gather_str))
            self.gather_tag = True
        else:
            conftest_str = "".join((db_login_str, '\n', code))


        conftest_obj = jinja2.Template(conftest_str)
        gather_res_data.update(login_data)  # 加入登录信息
        gather_res_data.update(config_data)
        content_str = conftest_obj.render(gather_res_data)  # 进行登陆参数、测试报告生成参数、所有配置参数替换

        # conftest_obj = jinja2.Template(content_str)  # 再次转换为可替换对象
        # content_str= conftest_obj.render(config_data)  # 后匹配所有配置信息

        config_data.pop('ac_config')  # 用完删除
        config_data.pop('config')
        config_data.pop('db_config')

        self.write_pytest_file(conftest_file_path, content_str)

    def make_pytest_file(self, test_file_path: str, login_fun: str, cases_data: dict, config_data: dict,
                         project_name: str) -> None:
        data = {
            "epic": "接口自动化",
            "project_name": project_name,
            "test_file_path": test_file_path,
            "case_data_all": cases_data,
            "project_tag": "scene_bao_app",
            "login_fun_str": login_fun,
            "config_data": config_data,

        }
        content = pytest_run_str.render(data)
        self.write_pytest_file(test_file_path, content)
