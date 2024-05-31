import logging
import os
import threading
from interface_runner.data_driver.common.project_path import log_conf_path, log_path
from interface_runner.data_driver.common.do_config import Config
import logging

__author__ = 'wangxueyi'
__date__ = '2020-09-27'

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class GetLog(object):
    '''
    日志类
    '''
    # _instance_lock = threading.Lock()  # 解决多线程下运行混乱问题
    # # def __init__(self):
    # #     pass
    #
    # def __init__(self,
    #              section="LEVEL",
    #              coOption="coLevel",
    #              outOption="outLevel",
    #              formatInfo="formatInfo",
    #              #name="ddt_interface_test",
    #              name="django",
    #              fileName=os.path.join(log_path, "logger.log")):
    #     '''
    #         coLevel为日志收集级别,outLevel为日志输出级别,formatInfo为日志输出格式，name为日志模块名，fileName为日志输出文件名
    #     '''
    #     Do_mkdir().do_project()  # 若没有log目录，先创建
    #     self.jd_logger = logging.getLogger(name)  # 定义日志收集模块的名字
    #     read = Config(os.path.join(ROOT_PATH, "config", "log.cfg"))  # 初始化
    #     # coLevel = read.get_str(section, coOption)
    #     if not self.jd_logger.handlers:  # 解决打印重复日志问题
    #         coLevel = read.get_str(section, coOption)
    #         self.jd_logger.setLevel(coLevel)  # 日志收集级别
    #         self.jd_filter = logging.StreamHandler()  # 过滤器
    #         outLevel = read.get_str(section, outOption)
    #         self.jd_filter.setLevel(outLevel)  # 日志输出级别
    #         # self.jd_logger.addHandler(self.jd_filter)         # 收集器与过滤器对接
    #         fh = logging.FileHandler(fileName, "a", encoding="utf-8")
    #         self.jd_logger.addHandler(fh)  # 导入收集器的日志到文件
    #         formatInfo = read.get_str(section, formatInfo)
    #         formatter = logging.Formatter(formatInfo)
    #         # self.jd_filter.setFormatter(formatter)  #过滤器日志输出级别处理后输出到控制台
    #         fh.setFormatter(formatter)  # 收集器输出级别处理后输出到文件
    #
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance'):  # 判断实例是否存在
    #         with GetLog._instance_lock:  # 多线程实例加锁
    #             if not hasattr(cls, '_instance'):
    #                 GetLog._instance = super().__new__(cls)
    #
    #     return GetLog._instance  # 返回实例

    def logger(self):
        #return self.jd_logger
        return logging.getLogger("run_case")


class Do_mkdir:

    def do_project(self):
        if not os.path.exists(log_path):  # 创建log目录
            os.makedirs(log_path)


if __name__ == "__main__":
    logConfFilePath = log_conf_path
    Do_mkdir().do_project()

    loggers = GetLog().logger()
    logger = GetLog().logger()

    logger.debug("test")  # 使用日志级别看自己，特别严重就用critical，一般错误就用error
    logger.info("test")
    logger.warning("test")
    logger.error("test")
    logger.critical("test")
