# coding:utf-8
from interface_runner.data_driver.logic.api_logic.agent_logic import agent_mgr_login_cmd, agent_mini_login_cmd
from interface_runner.data_driver.logic.api_logic.bmp_logic import bmp_mgr_login_cmd, bmp_mini_login_cmd
from interface_runner.data_driver.logic.api_logic.broker_logic.user_manager import fcb_app_login_pwd_cmd
from interface_runner.data_driver.logic.api_logic.middleend_logic.login import middleend_login_cmd
from interface_runner.data_driver.logic.api_logic.scene_logic.scene_bao_login_cmd import SceneLoginCmd
from interface_runner.data_driver.logic.api_logic.car_BYD_logic.car_BYD_mini_login_cmd import CarBYDMiniLoginCmd
import allure


class LoginInterface:
    """
         description：登录注册等相关接口
    """

    # description：APP密码登录接口
    # phone:手机号
    # pwd: 密码
    # os_type: 验证码类型 	MiniApp(小程序),MiniWeb（公众号），Web,IOS,Android_App,Android,Android_Pad
    # app_version: app版本号
    # os_version: 系统版本号
    # hardware_version:硬件版本
    # app_uuid: 设备唯一ID
    # jpushId:极光推送的设备ID
    # lbsCityCode:LBS定位到的城市站点Code
    # siteCityCode:用户选择的城市站点Code
    # return:{'status': 200, 'code': '0', 'message': 'success'}
    @allure.step("APP接口-B端接口登录")
    def app_login_broker_pwd(self, phone=None, pwd=None, os_type=None, app_version=None, os_version=None,
                             hardware_version=None, app_uuid=None, jpushId=None, lbsCityCode=None, siteCityCode=None,
                             terminalType=None, loginSelection=None):
        rec = fcb_app_login_pwd_cmd.FcbAppLonginPwd(terminalType=terminalType, loginSelection=loginSelection)
        out = rec.login_broker_pwd_cmd(phone=phone, pwd=pwd, os_type=os_type, app_version=app_version,
                                       os_version=os_version,
                                       hardware_version=hardware_version, app_uuid=app_uuid, jpushId=jpushId,
                                       lbsCityCode=lbsCityCode, siteCityCode=siteCityCode)
        return out

    @allure.step("APP接口-C端接口登录")
    def app_login_customer_pwd(self, phone=None, code=None, os_type=None, app_version=None, os_version=None,
                               hardware_version=None, app_uuid=None, jpushId=None, lbsCityCode=None, siteCityCode=None,
                               terminalType=None, loginSelection=None, registerFrom=None):
        rec = fcb_app_login_pwd_cmd.FcbAppLonginPwd(terminalType=terminalType, loginSelection=loginSelection)
        out = rec.login_customer_pwd_cmd(phone=phone, code=code, os_type=os_type, app_version=app_version,
                                         os_version=os_version,
                                         hardware_version=hardware_version, app_uuid=app_uuid, jpushId=jpushId,
                                         lbsCityCode=lbsCityCode,
                                         siteCityCode=siteCityCode, registerFrom=registerFrom)
        return out

    """
         description：运营后台登录成功接口
    """

    # count：验证码识别错误尝试登录次数
    # usr:登录账号
    # pwd: 密码
    # return:
    @allure.step("运营后台接口登录")
    def middleen_login_api_success(self, count, usr, pwd):
        rec = middleend_login_cmd.MiddleendLoginCmd()
        out = rec.middleend_login_successful_cmd(count=count, usr=usr, pwd=pwd)
        return out

    # username：会员经理管理平台登录账号
    # password:会员经理管理平台登录密码
    # return：{'status': 200, 'code': '000000', 'message': None, 'accessToken': 'eyJhbGciOiJSUzUxMiJ9.eyJzdWIiOiIxMzExMTExMTAiLCJleHAiOjE2MDUzMjA3NDd9.SGWuOxr8d12N3_JSFihrxkTLCvJn7DNFK0nDthNL985rIOnVVwzrUrLNXuXqlvez-nbXF8XudaL1OGmm7xHYW4MSDBmBNu3YIzv1AEqlrDHJ6YXhDRdWTenierCdWpuiGPTcNXKVkLLR_BYdlWCSrOb25Z6_JCiguDMmoE8JBlM'}
    @allure.step("会员经理管理平台接口登录")
    def web_bmp_mgr_login(self, username=None, password=None):
        rec = bmp_mgr_login_cmd.BmpMgrLoginCmd()
        out = rec.bmp_mgr_login_cmd(username=username, password=password)
        return out

    # username：会员经理小程序登录账号
    # password:会员经理小程序登录密码
    # return：{'status': 200, 'code': '000000', 'access_token': 'XXX'
    def bmp_mini_login(self, phone=None, pwd=None, os_type=None, app_version=None, os_version=None,
                       hardware_version=None, app_uuid=None):
        rec = bmp_mini_login_cmd.BmpMiniLoginCmd()
        out = rec.bmp_mini_login_cmd(phone=phone, pwd=pwd, os_type=os_type, app_version=app_version,
                                     os_version=os_version, hardware_version=hardware_version, app_uuid=app_uuid)
        return out

    # username：机构管理平台登录账号
    # password:机构管理平台登录密码
    # {'status': 200, 'code': '000000', 'message': None, 'accessToken': 'eyJhbGciOiJSUzUxMiJ9.eyJzdWIiOiJcIlRFU1QxMDE2XCIiLCJleHAiOjE2MDYwMTM0MjV9.etUWE0u-aHV4joM7HFgkTRwpG0GNCz2MQZdgNvpXeeX13URcFt-nT0uIk2ClJfiEeBJ8hMpDI3gQH-9nYgBhP2uHd9WsxHBjNEjPBj7_h9xXAWHEZ1G-kZ4MT2dJLS5Qb-EfEQuqW4U_nTmu8ipt7427wJNDk8XnEnLGWaiytxY', 'userId': 'TEST1016'}
    @allure.step("机构管理平台接口登录")
    def web_agent_mgr_login(self, username=None, password=None):
        rec = agent_mgr_login_cmd.AgentMgrLoginCmd()
        out = rec.agent_mgr_login_cmd(username=username, password=password)
        return out

    # username：机构小程序登录账号
    # password:机构小程序登录密码
    # return： {'status': 200, 'code': '000000', 'message': None, 'token': '78367367ff3b46cdae699cd7860d42d4', 'guid': '507558931290013698', 'brokerId': '507558931290013698', 'orgId': '6ee1b01bb4434a9d927191db68157ff3', 'unionId': 'HDB0010010001507558931290013698', 'myPhone': '13213123123'}
    @allure.step("机构小程序登录")
    def agent_mini_login(self, username=None, password=None):
        rec = agent_mini_login_cmd.AgentMiniLoginCmd()
        out = rec.agent_mgr_login_cmd(username=username, password=password)
        return out

    @allure.step("案场宝app登录")
    def scene_bao_login(self,username=None, password=None,pushId=None,terminalType=None):
        rec=SceneLoginCmd(terminalType)
        out=rec.scene_bao_login_cmd(username=username,password=password,pushId=pushId)
        return out

    @allure.step("汽车商城（BYD）mini登录")
    def car_BYD_mini_login(self, phone=None, smsCode=None, captcha=None, terminalType=None,os_type=None):
        rec = CarBYDMiniLoginCmd(terminalType,os_type)
        out = rec.car_BYD_mini_login_cmd(phone=phone, smsCode=smsCode, captcha=captcha)
        return out

if __name__ == "__main__":
    res = LoginInterface().car_BYD_mini_login(phone="19999900040", smsCode="111111", captcha="120c83f760a8c31e4ff")
    print(res)
