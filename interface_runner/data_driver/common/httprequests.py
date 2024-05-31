#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

import requests
import json
import base64
import urllib3
import allure
from requests.cookies import RequestsCookieJar
from interface_runner.data_driver.common.do_logs import GetLog

# —*-author:weisha -*-
# -*-date：2019-12-27-*-
urllib3.disable_warnings()
logger = GetLog().logger()


class HttpRequests():

    # def __init__(self):
    #     self.sessions=requests.session()
    # @Decorators.count_time
    def httpRequest(self, url, data, method, headers, product):
        res = None
        try:
            if method.upper() == "GET":  # upper小写转大写
                # logger.info("进行GET请求")
                request = requests.get(url=url, params=data, headers=headers, verify=False)
                null = None;
                false = False;
                true = True  # 兼容json返回结果中直接返回变量null问题
                res = json.dumps(request.text)
                # 兼容返回html、xml数据的情况
                try:
                    res = json.loads(eval(res))
                except Exception:
                    if request.status_code == 200:
                        pass
                    else:
                        raise Exception(f"error,when request method is get,status_code:"
                                        f"{request.status_code},\nresponse:{res}")
                return request.status_code, res

            elif method.upper() == "POST":
                if product == "mingyuan":
                    request = requests.post(url=url, data=data, headers=headers, verify=False)
                else:
                    request = requests.post(url=url, data=json.dumps(data), headers=headers, verify=False)

                null = None;
                false = False;
                true = True
                res = json.dumps(request.text)  # 解决部分response返回无法解析问题
                return request.status_code, json.loads(eval(res))

            elif method.upper() == "DELETE":
                request = requests.delete(url=url, data=data, headers=headers, verify=False)
                res = request.json()
                return request.status_code, res

            elif method.upper() == "PUT":
                request = requests.put(url=url, data=data, headers=headers, verify=False)
                res = request.json()
                return request.status_code, res

            elif method.upper() == "PATCH":
                request = requests.patch(url=url, data=json.dumps(data), headers=headers, verify=False)
                null = None;
                false = False;
                true = True
                res = json.dumps(request.text)  # 解决部分response返回无法解析问题
                return request.status_code, json.loads(eval(res))

            elif method.upper() == "UPLOAD":
                request = self.post_upload_file(url=url, data=data, headers=headers)
                res = json.dumps(request.text)  # 解决部分response返回无法解析问题
                return request.status_code, json.loads(eval(res))

            elif method.upper().split('.')[0] == "DOWNLOAD":
                request = self.get_download_file(url=url, data=data, headers=headers, method=method)
                # res = json.dumps(request.temp)  # 解决部分response返回无法解析问题
                return request.status_code, request.temp
            else:
                logger.warning("未知方法请求，请确认请求是否正确")

        except Exception as error:
            logger.error("接口发送请求时发生错误，原因：{}".format(error))
            logger.error("错误response:{}".format(res))
            raise error

    @allure.step('接口调用')
    def postMethod(self, url, data, headers):
        res = requests.post(url=url, data=json.dumps(data), headers=headers, verify=False)
        # allure.attach('response','{0},{1}'.format(res.status_code,json.loads(res.text)))
        return res.status_code, json.loads(res.text)

    def post_method_base64(self, url, data, headers=None):
        data_base64 = base64.b64encode(json.dumps(data).encode('utf-8')).decode("ascii")
        if headers != None:
            res = requests.post(url=url, data=json.dumps({'data': data_base64}), headers=headers)
        else:
            res = requests.post(url=url, data=data_base64, verify=False)
        return res.json()

    @allure.step('接口调用')
    def get_method(self, url, data, headers):
        res = requests.get(url=url, params=data, headers=headers, verify=False)
        return res

    def session(self):
        return requests.session()

    @allure.step('接口调用')
    def session_post(self, session, url, data, headers):
        # session =  requests.session()
        res = session.post(url=url, data=json.dumps(data), headers=headers, verify=False)
        allure.attach('response', '{0},{1}'.format(res.status_code, json.loads(res.text)))
        return res.status_code, json.loads(res.text)

    @allure.step('接口调用')
    def session_get(self, session, url, data, headers):
        # session = requests.session()
        res = session.get(url=url, params=data, headers=headers, verify=False)
        return res

    def get_system_cookies(self, session):
        '''通过request 登陆系统，获取cookie'''
        cookiesList = []
        loadCookies = requests.utils.dict_from_cookiejar(session.cookies)
        for cookieName, cookieValue in loadCookies.items():
            cookies = {}
            cookies['name'] = cookieName
            cookies['value'] = cookieValue
            cookiesList.append(cookies)
        return cookiesList

    def getcookies_decode_to_dict(self):
        current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        path = current_path + "\\data\\"
        if not os.path.exists(path):
            pass
            # loguru.logger.info('Cookie文件不存在')
        else:
            cookies_list = []
            # cookies_dict = {}
            cookies_str = ''
            with open(path + 'cookies.txt', 'r') as f:
                cookies = json.loads(f.read())
                for cookie in cookies:
                    # cookies_dict[cookie['name']] = cookie['value']
                    cookies_list.append(cookie['name'] + '=' + cookie['value'])
                    cookies_str = "; ".join(cookies_list)
                return cookies_str

    def getcookies_decode_to_cookiejar(self):
        current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        path = current_path + "\\data\\"
        if not os.path.exists(path):
            pass
            # loguru.logger.info('Cookie文件不存在')
        else:
            cookiejar = RequestsCookieJar()
            with open(path + 'cookies.txt', 'r') as f:
                cookies = json.loads(f.read())
                for cookie in cookies:
                    cookiejar.set(cookie['name'], cookie['value'])
                return cookiejar

    def post_upload_file(self, url, data, headers):
        """post方法上传文件:
        url:上传接口的url
        headers:请求头
        file_name:上传文件的名称,如：delete_middleend_case.xlsxpost_upload_filepost_upload_file
        file_absolute_path:上传文件的全路径，如：r'E:\FCB_Auto_Test\FCB_Auto_Test\data\delete_middleend_case.xlsx'
        content_type:上传的Content-Type，如：application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        """
        file_absolute_path = os.path.join(data_path, "files")
        try:
            files = {'file': open(os.path.join(file_absolute_path, data['file']), 'rb')}
            data.pop('file')  # 去除字典中的file关键值
        except Exception as error:
            logger.error("上传文件不存在，请检查文件是否上传到data->files目录下，或检查body的文件名是否正确")
            raise Exception("upload is error,no files found")

        if "Content-Type" in headers.keys():  # Content-Type需要删除，才能正常上传
            del headers["Content-Type"]

        request = requests.post(url=url, data=data, files=files, headers=headers)
        return request

    def get_download_file(self, url, data, headers, method):
        """
        下载文件到指定目录
        :param url: 文件下载的url
        :param file_path: 要存放的目录及文件名，例如：download/test.xls
        :return:
        """
        temp_res = {}  # 临时字典
        if not os.path.exists(down_path):  # 初始化文件下载目录
            os.makedirs(down_path)
        if method.upper().split('.')[1] == "POST":
            down_res = requests.post(url=url, data=json.dumps(data), headers=headers)
            suffix = down_res.headers["Content-Disposition"].split('.')[-1]  # 获取返回后缀名
            file_name = time.strftime("%Y%m%d%H%M%S.", time.localtime()) + suffix  # 组装文件名
        elif method.upper().split('.')[1] == "GET":
            down_res = requests.get(url)
            file_name = url.split('/')[-1]  # 获取文件名
        else:
            logger.warning("未知下载格式请求，请与自动化小组联系")
            raise Exception("Unknown download format,please check")

        try:
            file_path = os.path.join(down_path, file_name)  # 获取文件路径
            with open(file_path, 'wb') as file:
                file.write(down_res.content)
            temp_res["status"] = down_res.status_code  # status_code生成临时字典
            # temp_res["text"] = down_res.text  # text生成临时字典
            temp_res["text"] = "下载内容信息流，不做打印显示"
            down_res.temp = temp_res  # temp元组赋予临时返回值
        except Exception as error:
            logger.error("下载文件失败，请检查文件是否下载download目录下，或检查url链接是否正确")
            raise Exception("download is error,no files found")

        return down_res


if __name__ == "__main__":
    url = "http://middleend-sit-adminportal.fcb.com.cn/omc/prodmg/file/upload/compression"
    data = {
        "file": "agent.xlsx",
        "appWidth": "",
        "appHeight": "",
        "appSize": ""
    }
    headers = {}
    res = HttpRequests().httpRequest(url=url, method="upload", data=data, headers=headers)
    print(res)
