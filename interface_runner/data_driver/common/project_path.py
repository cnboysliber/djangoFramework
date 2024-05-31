import os

'''
用于系统目录路径获取方式管理文件
'''

# 读取项目路径
path_project = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

# 获取当前项目的配置目录env_info.cfg配置文件的路径

envInfo_conf_path = os.path.join(path_project, "config", "env_info.cfg")

public_info_path_sit = os.path.join(path_project, "config", "public", "public_sit.cfg")
public_info_path_sit2 = os.path.join(path_project, "config", "public", "public_sit2.cfg")
public_info_path_uat = os.path.join(path_project, "config", "public", "public_uat.cfg")

# #获取当前项目的配置目录case.conf配置文件的路径
# case_conf_path=os.path.join(path_project,"conf","case.cfg")

# 获取测试数据的路径
data_path = os.path.join(path_project, "data")

# 获取测试报告路径

test_result_path = os.path.join(path_project, "testReport")

# #获取日志配置文件路径
#
log_conf_path = os.path.join(path_project, "config", "log.cfg")

# 获取数据库登录配置
db_conf_path = os.path.join(path_project, "config", "log.cfg")

# 获取日志文件路径
project = os.path.split(path_project)[0]
log_path = os.path.join(project, "log")

# 获取文件下载路径
down_path = os.path.join(project, "download")

if __name__ == "__main__":
    ss = "E:\Auto\FCB_Auto_Test"
    res = os.path.split(ss)
    print(res)
    # print(os.path.join(data_path,"xx.xlsx"))
