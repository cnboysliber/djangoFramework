import pytest
import os
import shutil
from interface_runner.data_driver.common.data_process import GetCaseData as get_case
from interface_runner.data_driver.make.make_case import MakeCase


class RunCase:
    def __init__(self, user,report_name,save=False,id="未设置id"):
        self.Make = MakeCase(user,id)
        self.Make.gen_suit_work_dir()  # 初始化生成suit目录
        if report_name=="":
            self.report_name = self.Make.user_time_num   #调试时候的生成report名称
        else:
            self.report_name=report_name

        if save==True:
            self.Make.gen_report_dir(self.report_name)
        self.user=user

    def remove_file(self, path):
        if os.path.exists(path):  # 如果文件存在
            os.remove(path)

    def rm_pytest_dir(self):
        if os.path.exists(self.Make.suit_work_dir):
            shutil.rmtree(self.Make.suit_work_dir)  # 运行完删除文件

    def run_allure(self):
        os.system(self.Make.allure_report_command)


    def run_pytest_dir_gen_report(self):
        exec_list = ['-s', '-q', '--alluredir', self.Make.allure_results_dir,self.Make.suit_work_dir]
        pytest.main(exec_list)
        self.rm_pytest_dir()



    def run_pytest_dir(self):
        exec_list = ['-s',self.Make.suit_work_dir]
        pytest.main(exec_list)
        self.rm_pytest_dir()



    def run_main(self, cases_data, config_data, project_name, run_type):  # test为单个测试用例或单个测试套件，suits为多个测试套件
        conftest_file_path = self.Make.gen_conftest_file_path()
        test_file_path = self.Make.gen_pytest_file_path()
        self.Make.base_path = None  # 重置suit下的工作目录，下次运行重新生成，隔离每个suit数据
        if 'ac_config' in config_data.keys():  # 不存在账号配置时
            self.Make.make_conftest_file(conftest_file_path, config_data, project_name, self.report_name,
                                         config_data['ac_config']['fixture_code'], run_type, self.user)  # 生成conftest文件
        else:
            self.Make.make_conftest_file(conftest_file_path, config_data, "")
        self.Make.make_pytest_file(test_file_path, self.Make.login_fun, cases_data, config_data, project_name)  # 写文件

        # self.remove_file(test_file_path)

    # def run_main_websocket(self,cases_data,config_data,project_name):
    #     #out_list=[]
    #     test_file_path=self.Make.gen_pytest_file_path()
    #     self.Make.make_pytest_file(test_file_path,cases_data,config_data,project_name)  #写文件
    #     #pytest.main(["-s",test_file_path])
    #     #cmd=f'pytest -s {test_file_path}'
    #     cmd=f'python {test_file_path}'
    #     output_res=get_output_info(cmd)
    #     # for out in output_res:
    #     #     out_list.append(out)
    #     return output_res
    #     #self.remove_file(test_file_path)


if __name__ == "__main__":
    dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    ca = get_case(dir)
    case_data_all = ca.get_all_cases_data()
    id = "1111"
    RunCase(id).run_main(case_data_all)
