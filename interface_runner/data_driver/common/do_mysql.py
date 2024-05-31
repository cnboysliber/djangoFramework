import sys

import pymysql
import requests

from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.common.base import GetEnvInfo
from dbutils.pooled_db import PooledDB

logger = GetLog().logger()


class ExceteMysql:
    """
    执行mysql操作
    """

    def __init__(self, env, module_dict):
        # 初始化打开数据库
        if env not in ("uat"):
            self.module_list = []
            self.connect_list, self.true_Db, self.false_Db = [], [], []
            logger.info(f"数据库连接中，请稍等...")
            for module,db_info in module_dict.items():
                self.get_db_login(module,db_info)
                self.module_list.append(module)
            # 模块及连接状态k-y存入词典
            logger.info(f'数据库连接成功：{", ".join(self.true_Db)}')
            if self.false_Db:
                logger.info(f'数据库连接失败：{", ".join(self.false_Db)}')
            self.db_state = dict(
                map(lambda module, connect_state: [module, connect_state], self.module_list, self.connect_list))
        elif env in ("uat"):
            logger.info("请求环境为uat，不展示数据库打开状态")

    def get_db_login(self, module,db_info):
        try:
            pool = PooledDB(pymysql, 10, host=db_info['host'], user=db_info['user'], passwd=db_info['password'],
                            db=db_info['database'], port=int(db_info['port']), charset="utf8", ping=1)  # 10为连接池里的最少连接数
            db = pool.connection()
            self.connect_list.append(db)  # 添加已打开的数据库
            self.true_Db.append(module)
        except Exception as e:
            self.connect_list.append(e)  # 异常连接入列表
            self.false_Db.append(module)
            logger.error(module + f"异常:{e}")

    @staticmethod
    def get_uat_fetch_resp(url, module, sql, one=True):
        """
        通过服务获取uat的数据库结果
        """

        logger.info(f"模块：{module}，执行脚本：{sql}")
        try:
            body = {
                'db': module,
                'sql': sql,
                'one': one
            }
            logger.info(f'uat execute url={url}, body={body}')
            response = requests.post(url, json=body)
            if response.status_code != 200:
                raise Exception(f'uat获取sql返回值异常{response.status_code},{response.text}')
            return response.json()['_data']['retData']
        except Exception as e:
            logger.error(e)
        return

    # 查询返回单结果字典
    def get_fetch_dict(self, module, sql):
        logger.info(f"执行脚本：{sql}")
        # if sql[:6].upper() in ["INSERT", "UPDATE", "DELETE"]:
        #     self.exe_sql(module, sql)
        # else:
        with self.db_state[module].cursor(pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(sql)
                self.db_state[module].commit()  # 提交事物
                res = cursor.fetchone()
                if res is None:
                    con = self.get_oneopen_db(module)
                    cursor = con.cursor(pymysql.cursors.DictCursor)
                    cursor.execute(sql)
                    self.db_state[module].commit()  # 提交事物
                    res = cursor.fetchone()
                return res
            except Exception as error:
                info = sys.exc_info()
                logger.error(f"数据库执行错误{info[0]}={info[1]}")
                raise error

    # 查询返回多结果字典
    def get_fetch_dict_more(self, module, sql):
        logger.info("执行脚本：{}".format(sql))
        with self.db_state[module].cursor(pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(sql)
                self.db_state[module].commit()  # 提交事物
                res = cursor.fetchall()
                if res is None:
                    con = self.get_oneopen_db(module)
                    cursor = con.cursor(pymysql.cursors.DictCursor)
                    cursor.execute(sql)
                    self.db_state[module].commit()  # 提交事物
                    res = cursor.fetchall()
                return res
            except Exception as error:
                info = sys.exc_info()
                logger.error(f"数据库执行错误{info[0]}={info[1]}")
                raise error

    # 执行增、改、删
    # def exe_sql(self, module, sql):
    #     logger.info("执行脚本：{}".format(sql))
    #     try:
    #         cursor = self.db_state[module].cursor()
    #         exe_sql = cursor.execute(sql)
    #         if exe_sql == 0:
    #             con = self.get_oneopen_db(module)
    #             cursor = con.cursor()
    #             exe_sql = cursor.execute(sql)
    #         logger.warning("影响的行数：{}".format(exe_sql))
    #         self.db_state[module].commit()  # 提交事物
    #     except Exception as error:
    #         info = sys.exc_info()
    #         logger.error("数据库执行错误{}={}".format(info[0], info[1]))
    #         raise error

    # 打开单个数据库
    def get_oneopen_db(self, module):
        dataDb = GetEnvInfo().get_mysql_connect(module)
        pool = PooledDB(pymysql, 10, host=dataDb['host'], user=dataDb['user'], passwd=dataDb['password'],
                        db=dataDb['database'], port=int(dataDb['port']), charset="utf8")
        return pool.connection()

    # 关闭游标、退出数据库
    def exit_mysql(self):
        if GetEnvInfo().get_mysql_isopen() == "YES":
            for module in self.db_state:
                try:
                    self.db_state[module].cursor().close()
                    self.db_state[module].close()
                    logger.info("-" * 10 + f"关闭" + module + f"数据库" + "-" * 10)
                except Exception as e:
                    logger.error("-" * 10 + module + f"数据库打开异常，无需关闭:{e}")
        else:
            logger.info("-" * 10 + f"数据库开关未打开！" + "-" * 10)
