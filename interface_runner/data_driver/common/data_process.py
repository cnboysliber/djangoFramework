import random
import hashlib
import hmac
import os
import string
import time
import re
import copy
import datetime
from faker import Faker
from interface_runner.data_driver.common.do_enum import get_project
from interface_runner.data_driver.common.do_excel import DoExcel
from interface_runner.data_driver.common import do_config
from interface_runner.data_driver.common.do_logs import GetLog
from interface_runner.data_driver.common.project_path import envInfo_conf_path
from functools import wraps

logger = GetLog().logger()  # 引入日志模块

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
read = do_config.Config(ROOT_PATH + '/config/' + "log.cfg")  # 初始化
coLevel = read.get_str("LEVEL", "coLevel")
cache = {}  # 缓存字典


class RandomInfo:
    """
    description：随机获取用户相关信息
    """

    def __init__(self):
        self.fake = Faker()
        self.fake = Faker(locale='zh_CN')

    # 生成中文名字
    def get_china_name(self):
        return self.fake.name()

    # 生成手机号
    def getPhone(self):
        prelist = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
                   "147", "150", "151", "152", "153", "155", "156", "157", "158", "159",
                   "186", "187", "188", "189", "172", "176", "185"]
        return random.choice(prelist) + "".join(random.choice("0123456789") for i in range(8))

    def get_phone(self, number="185600011"):
        '''
        经纪中心使用的注册手机号，随机生成手机号
        :return: phone
        '''
        count = 11 - len(number)
        # number = do_config.Config(envInfo_conf_path).get_str("AUTO_PHONE", "phone")  # 获取配置文件里面的号码段
        phone = number + ''.join(str(i) for i in random.sample(range(0, 9), count))  # 号码段+随机生成多位数，参数count为随机生成count位数
        return phone

    def MD5(self, pwd="qwer1234"):
        '''
        MD5加密密码，并返回
        :return:
        '''
        # pwdStr = "qwer1234"
        m = hashlib.md5()
        m.update(pwd.encode("utf8"))
        return m.hexdigest()

    def md5_key(self, arg):
        hash = hashlib.md5()
        hash.update(arg.encode("utf-8"))
        return hash.hexdigest().lower()

    def get_authcode(self, data: dict) -> str:
        '''
        提供明源使用，获取authcode
        :param data:
        :return:
        '''
        sign = ""
        for key, value in data.items():
            if type(value) is not str:
                data[key] = str(value)  # 把list转化为字符串
            else:
                pass
        resList = sorted(data.items(), key=lambda d: d[0])
        for value in resList:
            sign = sign + value[1]
        authcode = self.md5_key(sign)
        return authcode

    def get_hmacsha265_sign(self, key, timestamp, access_token, union_id, strTime="timestamp=", strToken="&token=",
                            strUnionId="&unionId="):
        '''
        HMAC+SHA256加密，并返回
        :return: sign
        '''
        sign = hmac.new(key.encode(), (strTime + timestamp + strToken + access_token + strUnionId +
                                       union_id).encode(), digestmod=hashlib.sha256).hexdigest().upper()  # sign 加密
        return sign

    def get_sign(self, publicDict, project, timestamp=None, sceneKey="hdbscene", bcKey="hdboms"):
        '''
        根据项目和登录信息，获取项目对应sign,若对应项目有多个登录账号，则是以sign_type区分sign
        :param publicDict: 登录信息字典
        :param project:  项目
        :return:
        '''
        signDict = {}

        if timestamp == None:  # 兼容函数自己传时间戳的情况
            pass
        else:
            publicDict["timestamp"] = timestamp  # 优先使用函数自己的传的时间戳

        for key, value in publicDict.items():
            if project in ("scene_bao_app"):
                if 'ut' in key:
                    if '_' in key:  # 解决多个账号生成sign
                        sValue = key.split('_')
                        signDict["sign_" + sValue[1]] = self.get_hmacsha265_sign(sceneKey, publicDict["timestamp"],
                                                                                 publicDict[key],
                                                                                 publicDict["userId_" + sValue[1]],
                                                                                 strTime="timestamp=",
                                                                                 strToken="&token=",
                                                                                 strUnionId="&brokerId=")
                    else:
                        signDict["sign"] = self.get_hmacsha265_sign(sceneKey, publicDict["timestamp"],
                                                                    publicDict[key],
                                                                    publicDict["userId"],
                                                                    strTime="timestamp=",
                                                                    strToken="&token=",
                                                                    strUnionId="&brokerId=")
            elif project in ("fcb_broker_app", "fcb_customer_app"):
                if 'token' in key:
                    if '_' in key:  # 解决多个账号生成sign
                        sValue = key.split('_')
                        if len(sValue) == 3:
                            signDict["sign_" + sValue[2]] = self.get_hmacsha265_sign(bcKey, publicDict["timestamp"],
                                                                                     publicDict[key],
                                                                                     publicDict[
                                                                                         "union_id_" + sValue[2]])
                        if len(sValue) == 2:
                            signDict["sign"] = self.get_hmacsha265_sign(bcKey, publicDict["timestamp"],
                                                                        publicDict[key],
                                                                        publicDict["union_id"])
        return signDict

    def get_sign_tag(self, publicDict: dict, project: str, tag: list) -> dict:
        '''
        支持多项目登录逻辑生成sign
        '''
        if tag != []:
            publicDict[tag[0]]["timestamp"] = publicDict["timestamp"]  # 迁移时间戳进入需要的登录态项目
            if tag[0].upper() in ("CUS", "BRO", "SCE"):
                if tag[0].upper() in ("CUS", "BRO"):
                    project = "fcb_broker_app"  # 若为c或b端，则直接已B端的project去获取，因b、c端生成sign规则一致
                    signRes = self.get_sign(publicDict[tag[0]], project)
                    publicDict[tag[0]].update(signRes)
                if tag[0].upper() in ("SCE"):
                    project = "scene_bao_app"
                    signRes = self.get_sign(publicDict[tag[0]], project)
                    publicDict[tag[0]].update(signRes)

            else:
                logger.warning(f"不支持项目:{tag[0]} sign生成，请检查是否存在此项目，或联系自动化小组成员添加")
        else:
            publicDict = self.get_sign(publicDict, project)

        return publicDict

    # 生成身份证号
    def get_id_card(self):
        return self.fake.ssn()

    def HK_card(self):
        '''
        香港身份证号生成
        :return:
        '''
        indexObj = None
        EngList = list(string.ascii_uppercase)
        EngObj = random.choice(EngList)
        for index, value in enumerate(EngList):
            if EngObj == value:
                indexObj = index
        sixNum = self.get_random_num(6)
        m = 7
        sumObj = 0
        for num in list(sixNum):
            sumObj = sumObj + int(num) * m
            m = m - 1
        remainder = ((indexObj + 1) * 8 + sumObj) % 11
        if remainder == 1:
            card = ''.join((EngObj, sixNum, "(A)"))
        elif remainder == 0:
            card = ''.join((EngObj, sixNum, "(0)"))
        else:
            card = ''.join((EngObj, sixNum, f"({11 - remainder})"))

        return card

    #
    # for i in range(10):
    #     card=HK_card()
    #     print(card)
    #     match=re.search("^[A-Z]{1,2}[0-9]{6}\\(?[0-9A]\\)?$",card)
    #
    #     print(match)

    def AM_card(self):
        '''
        生成澳门身份证号
        :return:
        '''
        firstList = [1, 5, 7]
        middleNum = self.get_random_num(6)
        EngObj = string.ascii_uppercase
        endList = list(range(0, 10)) + list(EngObj)
        card = ''.join((str(random.choice(firstList)), middleNum, str(random.choice(endList))))
        return card

    def TW_card(self):
        '''
        生成台湾身份证号
        :return:
        '''
        EngList = list(string.ascii_uppercase)
        num = self.get_random_num(9)
        card = ''.join((random.choice(EngList), str(num)))
        return card

    def get_random_name(self, strData="AUTO"):
        """随机生成一个固定字母+时分秒 的字符串"""
        # now_time = time.strftime("%Y%m%d/%H%M%S", time.localtime())
        now_time = time.strftime("%H%M%S", time.localtime())
        return strData + str(now_time)

    def get_random_ln(self, letter=3, number=6):
        '''
        获取随机位数的字母和数字.string.digits只能随机10的数字，每多出10就翻倍
        :return:
        '''
        temp_number = ""
        for count in range(0, number // 10 + 1):
            temp_number = temp_number + string.digits
        res = ''.join(random.sample(string.ascii_letters, letter) + random.sample(temp_number, number))
        return res

    def get_random_num(self, number=6):
        '''
        获取随机位数数字
        获取随机位数数字,string.digits只能随机10的数字，每多出10就翻倍
        :return:
        '''
        # res=''.join(random.sample(string.digits,number))
        temp_number = ""
        for count in range(0, number // 10 + 1):
            temp_number = temp_number + string.digits
        res = ''.join(random.sample(temp_number, number))
        return res

    def get_random_let(self, letter=6):
        '''
        获取随机位数的字母
        :return:
        '''
        res = ''.join(random.sample(string.ascii_letters, letter))
        return res

    # 生成一个用户概貌
    def get_profile(self):
        return self.fake.simple_profile(sex=None)

    def get_time(self, count, tag, format='%Y-%m-%d %H:%M:%S'):
        '''
        根据输入的天数，计算当前时间减去或者加上输入的天数，得出计算后的时间
        :param count:
        :param tag:
        :return:
        '''
        nowTime = datetime.datetime.now()
        dataCount = datetime.timedelta(days=count)
        if tag == "-":
            resTime = (nowTime - dataCount).strftime(format)
        elif tag == "+":
            resTime = (nowTime + dataCount).strftime(format)
        else:
            logger.warning("不支持此种数据运算格式，仅支持加减 + -")
        return resTime

    def get_date(self, count, tag):
        '''
        根据输入的天数，计算当前时间减去或者加上输入的天数，得出计算后的时间
        :param count:
        :param tag:
        :return:
        '''
        nowTime = datetime.datetime.now()
        dataCount = datetime.timedelta(days=count)
        if tag == "-":
            resTime = (nowTime - dataCount).strftime('%Y-%m-%d')
        if tag == "+":
            resTime = (nowTime + dataCount).strftime('%Y-%m-%d')
        return resTime

    def get_timestamp(self, num):
        '''
        根据输入的位数，计算当前时间时间戳
        :param num: 时间戳位数
        :return:int(num) 返回时间戳位数
        '''
        if isinstance(num, int) and num > 0:
            t = round(time.time() * pow(10, num - 10))
            return int(t)
        else:
            logger.warning("输入为：{}，只支持正整数，请重新输入！".format(num))

    def auto_product_in(self, autoKey: str):
        '''
        自动生成数据
        :param autoKey:
        :return:
        '''
        dataDict = {}
        if "china_name" in autoKey:
            name = self.get_china_name()
            dataDict[autoKey] = name
        elif "broker_phone" in autoKey:
            broker_phone = self.get_phone()
            dataDict[autoKey] = broker_phone
        elif "phone" in autoKey:
            phone = self.get_phone()
            dataDict[autoKey] = phone
        elif "mobile" in autoKey:
            mobile = self.getPhone()
            dataDict[autoKey] = mobile
        elif "random_name" in autoKey:
            random_name = self.get_random_name()
            dataDict[autoKey] = random_name
        elif "pwd" in autoKey:
            pwdMD5 = self.MD5()
            dataDict[autoKey] = pwdMD5
        elif "id_card" in autoKey:  # 获取完整身份证号
            id_card = self.get_id_card()
            dataDict[autoKey] = id_card
        elif "cert_six" in autoKey:  # 自动生成身份证后6位
            cert_no = str(self.get_id_card())[-6:]
            dataDict[autoKey] = cert_no
        elif "letter_six" in autoKey:  # 自动生成6位字母，不分大小写
            letter_six = ''.join(random.sample(string.ascii_letters, 6))
            dataDict[autoKey] = letter_six
        elif "ld_nine" in autoKey:  # 自动生成3位字母+6位数字，不分大小写
            ld_nine = ''.join(random.sample(string.ascii_letters, 3) + random.sample(string.digits, 6))
            dataDict[autoKey] = ld_nine
        elif "HK_card" in autoKey:
            HK_card = self.HK_card()
            dataDict[autoKey] = HK_card
        elif "TW_card" in autoKey:
            TW_card = self.HK_card()
            dataDict[autoKey] = TW_card
        elif "AM_card" in autoKey:
            AM_card = self.AM_card()
            dataDict[autoKey] = AM_card
        else:
            logger.warning("自动生成数据未匹配到key:{}，请联系自动化小组成员进行补充！".format(autoKey))
        return dataDict

    def auto_product_data(self, data: str, relevantParamsFun) -> dict:
        '''
        根据传进来的字典的key值，自动生成对应的value
        '''
        dataDict = {}  # 用于存放生成的键值对数据
        random = RandomInfo()
        resultList = DataProcess().str_processor_for_auto(data)  # 对字符串进行处理，包括去空格，去换行符，并以英文分号;切割成list返回
        resultList = eval(relevantParamsFun(str(resultList), "autoProduct"))  # 执行参数替换逻辑
        for autoKey in resultList:
            if type(autoKey) is tuple:
                for index, paramsValue in enumerate(autoKey[2]):
                    try:
                        if type(eval(paramsValue)) is int:  # 针对全为数字的字符串，不执行解封操作
                            pass
                        else:
                            autoKey[2][index] = eval(paramsValue)  # 解封字符串
                    except Exception:
                        pass
                res = Reflex().get_fun(random, fun=autoKey[1], paramsValues=autoKey[2])  # 搜索函数并获取结果
                dataDict[autoKey[0]] = res
            else:
                data = self.auto_product_in(autoKey)
                dataDict.update(data)

        return dataDict


class DataProcess:
    '''
    数据处理类，比如处理字符串
    '''

    def __init__(self):
        self.tag = None

    def str_processor_for_auto(self, data: str) -> list:
        '''
        处理字符串，包括去换行符、去空格，最后根据英文分号返回list
        :return: list
        '''
        # delLF = data.replace('\n', '')  # 去掉换行符
        # delBlank = delLF.replace(' ', '')  # 去掉空格
        keyList = []
        result = data.split(";")  # 以英文分号隔开
        for value in result:
            value = value.strip()
            if "=" in value:
                data_split = value.split('=')
                try:
                    if data_split[1].replace(' ', '') == '':
                        keyList.append(data_split[0])
                except:
                    res = self.split_autoProduct(value)  # 是个tuble
                    keyList.append(copy.deepcopy(res))
            else:
                keyList.append(value)

        return keyList

    def types(self, data):
        '''
        处理type，提取type里面的数据类型
        :param data:
        :return:
        '''
        data = str(type(data))
        res = re.findall(r"\'([\s\S]+?)\'", data)[0]
        return res

    def get_iterator(self, iterator):
        '''
        获取迭代器的结果
        :param iterator:
        :return:
        '''
        try:
            res = iterator.__next__()
            return res
        except Exception:
            return None

    def str_replace(self, data, tag=None):
        '''
        把传入的值的中文标点，默认替换为英文标点，以及去空格、换行符
        :param data: 需要替换中文标点的str obj
        :return: data
        '''
        # intab='：；，。！？【】“（）％＃＠＆１２３４５６７８９０'  #中文标点
        # outtab=':;,.!?[]"()%#@&1234567890'  #英文标点
        chinaTab = ['：', '；', '，', '。', '！', '？', '【', '】', '“', '（', '）', '％', '＃', '＠', '＆', "’", ' ', '\n', '”']
        englishTab = [':', ';', ',', '.', '!', '?', '[', ']', '"', '(', ')', '%', '#', '@', '&', "'", '', '', '"']
        for index in range(len(chinaTab)):
            if chinaTab[index] in data:
                if chinaTab[index] == tag:
                    if tag == ' ':
                        data = data.strip()
                    else:
                        pass
                else:
                    data = data.replace(chinaTab[index], englishTab[index])
        return data

    def split_for_save(self, data):
        '''
        提供给excel读取出来的save字段切割使用
        :param data: assert或save的数据
        :return: listObj   嵌套dict
        '''
        listObj = []
        data = data.split(";")  # 第一次根据;分割
        for dataValue in data:
            dictObj = {}
            if dataValue == "":  # 兼容防止;后面出现空的信息
                pass
            else:
                res = dataValue.split("=", 1)  # 第二次根据=分割，仅切割一次，防止误切割
                for index in range(len(res)):
                    res[index] = res[index].strip()  # 去前后空格处理
                    try:
                        result = eval(res[index])  # 防止出现嵌套字符串如"'000000'"
                        res[index] = result  # 重新赋值
                    except Exception:
                        pass
                    if index == 0:
                        dictObj["key"] = res[index]
                    if index == 1:
                        extractValue = self.assert_extract(res[index])
                        if extractValue == None:
                            dictObj["jsonPath"] = res[index]
                        else:
                            dictObj["jsonPath"] = extractValue[0]
                            dictObj["index"] = extractValue[1]

                listObj.append(copy.deepcopy(dictObj))

        return listObj

    def split_autoProduct(self, data: str) -> tuple:
        '''
        切割包含函数参数的autoProduct字符串
        :param data:
        :return:
        '''
        data_split = data.split("=")
        key = data_split[0].strip()
        fun = re.findall(r'\=([\s\S]+?)\(', data)[0].strip()  # 去前后空格
        res = re.findall(r'\(([\s\S]+?)\)', data)
        if res != []:
            paramsValues = res[0].split(",")
            for index in range(len(paramsValues)):
                paramsValues[index] = paramsValues[index].strip()
                try:
                    paramsValues[index] = eval(paramsValues[index])  # 去除双引号
                except:
                    pass
            return key, fun, paramsValues
        else:
            paramsValues = []
            return key, fun, paramsValues

    # def split_for_assert(self,data):
    #     '''
    #     给从excel里读取出来的断言数据进行处理，返回一个字典，字典的每个value均为嵌套list
    #     :param data: assert数据
    #     :return:
    #     '''
    #     dictObj = {}
    #     assertKey = ["||", "!=", "=", "not in","in"]  # 切割分先后，不能调换key的顺序
    #     data = data.split(";")  # 第一次根据;分割
    #     for key in assertKey:  # 给字典赋值
    #         dictObj[key] = []
    #
    #     for dataValue in data:
    #         for keyValue in assertKey:
    #             if keyValue.replace(" ","") in dataValue.replace(" ",""):  #去空格比较
    #                 if keyValue in ("||"):
    #                     res = dataValue.split(keyValue)  # 根据or或者||分割
    #                     orList = []
    #                     for orValue in res:
    #                         res = self.split_for_assert(orValue)  # 递归
    #                         for key in res.keys():  # 再做一次提取
    #                             value = res[key][0]
    #                             res[key] = value  # 重新赋值
    #                         orList.append(res)  # 用于存放每次返回的字典
    #                     dictObj[keyValue].append(copy.deepcopy(orList))
    #                     break
    #                 else:
    #                     #res = dataValue.split(keyValue)  # 第二次根据key分割
    #                     res=self.assert_process(dataValue,keyValue)  #解决in、not in 误切割
    #                     if res != None:
    #                         for index in range(len(res)):
    #                             res[index] = res[index].strip()  # 去空格处理
    #                             try:
    #                                 result = eval(res[index])  # 防止出现嵌套字符串如"'000000'"，并去前后空格
    #                                 res[index] = result  # 重新赋值
    #                             except Exception:
    #                                 pass
    #                         dictObj[keyValue].append(copy.deepcopy(res))
    #                         break
    #                     else:
    #                         pass
    #
    #     for key in list(dictObj):
    #         if dictObj[key] == []:
    #             dictObj.pop(key)  # 去除为空[]的value
    #
    #     return dictObj
    def split_for_assert(self, data):
        '''
        给从excel里读取出来的断言数据进行处理，返回一个字典，字典的每个value均为嵌套list
        :param data: assert数据
        :return:
        '''
        dictObj = {}
        assertKey = ["||", "!=", "=", "not in", "in"]  # 切割分先后，不能调换key的顺序
        data = data.split(";")  # 第一次根据;分割
        for key in assertKey:  # 给字典赋值
            dictObj[key] = []

        for dataValue in data:
            for keyValue in assertKey:
                if keyValue.replace(" ", "") in dataValue.replace(" ", ""):  # 去空格比较
                    if keyValue in ("||"):
                        res = dataValue.split(keyValue)  # 根据or分割
                        orList = []
                        for orValue in res:
                            res = self.split_for_assert(orValue)  # 递归
                            for key in res.keys():  # 再做一次提取
                                value = res[key][0]
                                res[key] = value  # 重新赋值
                            orList.append(res)  # 用于存放每次返回的字典
                        dictObj[keyValue].append(copy.deepcopy(orList))
                        break
                    else:
                        # res = dataValue.split(keyValue)  # 第二次根据key分割
                        res = self.assert_process(dataValue, keyValue)
                        if res != None:
                            resDict = {}
                            for index, value in enumerate(res):
                                res[index] = value.strip()
                                try:
                                    result = eval(value)  # 防止出现嵌套字符串如"'000000'"，并去前后空格
                                    res[index] = result  # 重新赋值
                                except Exception:
                                    pass

                                if index == 0:
                                    resDict["expectRes"] = res[index]
                                if index == 1:
                                    extractValue = self.assert_extract(res[index])  # 处理存在|需要再次提取的情况
                                    if extractValue == None:
                                        resDict["jsonPath"] = res[index]
                                    else:
                                        resDict["jsonPath"] = extractValue[0]
                                        resDict["index"] = extractValue[1]

                            dictObj[keyValue].append(copy.deepcopy(resDict))
                            break
                        else:
                            pass

        for key in list(dictObj):
            if dictObj[key] == []:
                dictObj.pop(key)  # 去除为空[]的value

        return dictObj

    def assert_extract(self, jsonPathData: str):
        '''
        assert、save再次提取，使用|切割
        '''
        if "|" in jsonPathData:
            res = jsonPathData.split("|")
            try:
                index = int(res[1].strip())
            except Exception:
                index = res[1].replace(" ", "")
                # logger.error(f"不支持非整型int数据：{res[1].strip()}，请修正为整型数据int类型")
            jsonPath = res[0].strip()
            return jsonPath, index



        else:
            return None

    def assert_process(self, data: str, keyValue: str) -> list:
        '''
        断言切割处理
        :param data:  断言字符串
        :param keyValue: 断言key
        :return:
        '''
        res = None
        obj = ["not in", "in"]  # 仅对in类型断言进行处理
        splitList = data.split("$")
        splitLeft = splitList[0].replace(" ", "")  # 左边的字符串，去除空格
        splitRight = splitList[1].strip()
        if keyValue in obj:
            keyValue = keyValue.replace(" ", "")  # 去空格
            if keyValue == "in":  # in断言特殊处理
                if splitLeft[-1] in ('"', "'"):  # 兼容"$..code"的$前面存在双引号的情况
                    if keyValue == splitLeft[-3:-1]:
                        data = "".join(
                            (splitLeft[0:-3], keyValue.upper(), splitLeft[-1], '$', splitRight))  # 把分割值转化为大写拼接后再分割
                        res = data.split(keyValue.upper())
                        return res
                else:
                    if keyValue == splitLeft[-2:]:
                        data = "".join((splitLeft[0:-2], keyValue.upper(), "$", splitRight))  # 把分割值转化为大写拼接后再分割
                        res = data.split(keyValue.upper())
                        return res
            if keyValue == "notin":  # notin 断言特殊处理
                if splitLeft[-1] in ('"', "'"):  # 兼容"$..code"的$前面存在双引号的情况
                    if keyValue == splitLeft[-6:-1]:
                        data = "".join((splitLeft[0:-6], keyValue.upper(), splitLeft[-1], "$", splitRight))
                        res = data.split(keyValue.upper())
                        return res
                else:
                    if keyValue == splitLeft[-5:]:
                        data = "".join((splitLeft[0:-5], keyValue.upper(), "$", splitRight))  # 把分割值转化为大写拼接后再分割
                        res = data.split(keyValue.upper())
                        return res
        else:
            res = data.split(keyValue)  # 第二次根据key分割
            return res

    def get_case_project_data(self, caseData):
        '''
        传入用例数据，根据用例数据，切割路径，并根据路径获取枚举类中的项目名称
        :param caseData: 用例数据
        :return: excel的每行数据，项目名称
        '''
        for key, value in caseData.items():
            directory = os.path.split(key)[1]  # 切割路径，返回元组，获取元组里面的目录
            if directory == "broker":
                project = get_project.broker.value
            elif directory == "customer":
                project = get_project.customer.value
            elif directory == "om":
                project = get_project.om.value
            elif directory == "prod":
                project = get_project.prod.value
            elif directory == "middleend":
                project = get_project.middleend.value
            elif directory == "agent_manager":
                project = get_project.agent_manager.value
            else:
                # logger.info("无此用例目录，请联系自动化小组成员添加")
                project = directory
        return value, project


class GetCaseData:
    """
    description:获取接口自动化excel用例数据
    """

    def __init__(self, dir):  # 输入指定目录
        self.dir = dir
        logger.info("excel文件路径{}".format(dir))
        self.resDict = {}
        self.elseDict = {}

    # def get_excel_lists(self):
    #     '''
    #     获取某个目录下所有xlsx文件路径
    #     :return: 文件路径的list
    #     '''
    #     excel_list = []
    #     for home, dirs, files in os.walk(self.dir):
    #         for filename in files:
    #             f = re.findall(r'^([\W\w]*\.xlsx)$', filename)  # 通过正则获取指定目录下所有xlsx文件
    #             if f != []:
    #                 if "~$" in f[0][0:2]:
    #                     pass
    #                 else:
    #                     full_name = os.path.join(home, f[0])  # 拼接路径，返回具体的xlsx文件path
    #                     excel_list.append(full_name)
    #     return excel_list

    def get_excel_dict(self, dir):  # 递归函数，无法使用初始化的dir
        '''
        获取指定目录下所有xlsx文件，按目录路径为key，xlsx文件为value返回
        :return: 字典
        '''
        global flist
        lsdir = os.listdir(dir)  # 获取目录下所有文件及目录名称
        dirs = [i for i in lsdir if os.path.isdir(os.path.join(dir, i))]  # 返回所有目录名称
        flist = []
        if dirs:
            for i in dirs:
                # url = os.path.join(self.dir, i)
                self.get_excel_dict(os.path.join(dir, i))
        files = [i for i in lsdir if os.path.isfile(os.path.join(dir, i))]
        for file in files:
            f = re.findall(r'^([\W\w]*\.xlsx)$', file)  # 通过正则获取指定目录下所有xlsx文件
            if f != []:
                if "~$" in f[0][0:2]:
                    pass
                else:
                    full_name = os.path.join(dir, f[0])  # 拼接路径，返回具体的xlsx文件path
                    flist.append(full_name)
        self.elseDict[dir] = copy.deepcopy(flist)
        for key, value in self.elseDict.items():
            if value != []:  # 把非空的值添加到另外一个字典里面
                self.resDict[key] = value
        return self.resDict

    def get_sheet_list(self, excel_name):
        '''
        获取指定xlsx文件的所有sheets
        :param excel_name:  xlsx文件名称
        :return: sheets 列表
        '''
        self.ex = DoExcel(excel_name)
        sheets = self.ex.get_sheet_name()
        return sheets
        # self.ex.excel_close()

    def get_login_tag(self, data: str) -> list:
        '''
        获取登录标识
        '''
        params = re.findall(r'\${([\s\S]+?)\}', data)
        resList = []
        for value in params:
            if "." in value:
                loginTag = value.split(".")[0]
                resList.append(loginTag)
            else:
                pass
        return list(set(resList))

    def case_data_processor(self, case_info):
        '''
        对用例数据进行处理，把字符串里面的中文标点统一替换为英文标点，以及去空格、换行符等
        :param case_info:
        :return:
        '''
        case_info["interfacePath"] = DataProcess().str_replace(str(case_info["interfacePath"]))
        case_info["headers"] = DataProcess().str_replace(str(case_info["headers"]))
        # case_info["body"] = DataProcess().str_replace(str(case_info["body"]),tag=' ')
        case_info["autoProduct"] = DataProcess().str_replace(str(case_info["autoProduct"]), tag=' ')
        case_info["save"] = DataProcess().str_replace(str(case_info["save"]), tag=' ')
        # case_info["assert"] = DataProcess().str_replace(str(case_info["assert"]), tag=' ')
        case_info["product"] = DataProcess().str_replace(str(case_info["product"]))

        case_info["loginTag"] = self.get_login_tag(case_info["headers"])  # 获取请求头里面的登录tag

        return case_info

    def get_case_data(self, sheet):
        '''
        从xlsx获取指定sheet的数据
        :param sheet: sheet
        :return: 嵌套字典
        '''
        self.priority = do_config.Config(envInfo_conf_path).get_str("PRIORITY", "priority")
        try:
            list_data = []
            all_case_info = self.ex.get_listdict_all_value(sheet)
            self.ex.excel_close()  # 读取完用例关闭excel
            for case_info in all_case_info:
                if self.priority.upper() == "ALL":  # 按用例优先级过滤
                    case_info = self.case_data_processor(case_info)
                    yield case_info
                else:
                    if case_info["priority"].upper() == self.priority.upper():  # 按用例优先级过滤
                        case_info = self.case_data_processor(case_info)
                        yield case_info

        except Exception as e:
            logger.error("路径{}：读取xlsx文件失败".format(self.dir))
            raise e

    def get_all_cases_data(self):
        '''
        循环遍历所有xlsx文件，并遍历对应文件的sheet，xlsx文件路径为key，对应的xlsx文件的每个sheet页的每行字典数据为value返回
        :return: 嵌套字典
        '''
        # excel_list = self.get_excel_list()
        # for excel in excel_list:
        #     sheets = self.get_sheet_list(excel)
        #     for sheet in sheets:
        #         # data_list = list(self.get_case_data(sheet))
        #         data_list = self.get_case_data(sheet)
        #         for items in data_list:
        #             yield items
        dir = self.dir
        res_list = []
        excel_dict = self.get_excel_dict(dir)
        for key, value in excel_dict.items():
            for excel in value:
                sheets = self.get_sheet_list(excel)
                for sheet in sheets:
                    # data_list = list(self.get_case_data(sheet))
                    data_list = self.get_case_data(sheet)
                    for items in data_list:
                        items["excelPath"] = excel  # 添加用例文件路径到测试数据
                        items["excelSheet"] = sheet
                        resDict = {}
                        resDict[key] = items
                        result = copy.deepcopy(resDict)  # xlsx文件路径为key，对应的xlsx文件的每个sheet页的每行字典数据为value返回
                        res_list.append(result)

        return res_list


class Reflex:
    '''
    获取函数
    '''

    def get_fun(self, *objs: object, fun: str, paramsValues: list):
        '''
        获取函数并运行
        :param fun:
        :param paramsValues:
        :return:
        '''
        for obj in objs:
            if hasattr(obj, fun):
                fun = getattr(obj, fun)
                if paramsValues != []:
                    res = fun(*paramsValues)
                    return res
                else:
                    res = fun()
                    return res
            else:
                logger.warning("不存在这个函数,请确认是否有写错函数名，或者联系自动化小组添加新功能函数")


class Decorators():
    '''
    装饰器类
    '''

    @staticmethod
    def try_dec(fun):
        # @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            try:
                fun(*args, **kwargs)
                # print("我是装饰器")
            except Exception as e:
                logger.error("类函数{}运行过程中发生错误：{}".format(fun.__name__, e))
                raise e

        return wrapper

    @staticmethod
    def add_log(fun):  # 仅提供给运行用例使用
        def wrapper_log(self, case_data):
            if coLevel in ("WARNING"):
                logger.warning("请求接口:{}".format(case_data["interfaceName"]))
            res = fun(self, case_data)
            return res

        return wrapper_log

    @staticmethod
    def count_time(fun):
        '''
        统计函数运行时间装饰器
        '''

        def wrapper_time(*args, **kwargs):
            start = time.time()
            res = fun(*args, **kwargs)
            end = time.time()
            useTime = end - start
            logger.info("函数:{}运行时间为:{}s".format(fun.__name__, useTime))
            return res

        return wrapper_time

    @staticmethod
    def has_fun(tag: str = None):
        def has_funs(func):
            '''
            只允许函数运行一次，后面每次运行都会直接返回第一次运行时候的结果
            '''

            @wraps(func)
            def warps_func(*args, **kwargs):
                # 函数的名称作为key
                key = func.__name__
                # 判断是否存在缓存
                if key in cache.keys():
                    if tag == "login":
                        pass
                        # logger.info("****else login:该项目已进行过登录，现直接获取上次登录的结果****")
                    result = cache[key]
                else:
                    result = func(*args, **kwargs)
                    cache[key] = result
                return result

            return warps_func

        return has_funs


if __name__ == "__main__":
    # data = RandomInfo().get_time(30,"+",'%m-%d %H:%M:%S')
    data = RandomInfo().get_time(10, '-', "%Y.%m.%d %H:%M:%S")
    print(data)
    # funA(10)
