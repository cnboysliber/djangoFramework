# coding:utf-8
import allure


class InterfaceRecommend:
    """
          description：APP推荐接口
          :Authorization:接口消息头中Authorization
          :union_id: 接口消息头中union_id
          :brokerid:接口消息头中brokerId
          :cstName:客户姓名
          :mobileNo: 客户手机号
          :certNo: 身份证后六位
          :intentionBuildingId: 意向楼盘ID
          :arriveBuildingId: 联销盘到访楼盘ID
          :needDetail: 客户购房需求
          :planDate: 预约看房日期
          :remark: 备注
          :return:
    """
    @allure.step("APP接口-推荐客户")
    def broker_recommend(Authorization, union_id, brokerid, cstName=None, mobileNo=None, certNo=None, intentionBuildingId=None,
                         arriveBuildingId=None, needDetail=None, planDate=None, remark=None):
        rec = recommend_customer_cmd.RecommendCmd(Authorization, union_id, brokerid)
        return rec.broker_recommend_cmd(cstName=cstName, mobileNo=mobileNo, certNo=certNo, intentionBuildingId=intentionBuildingId,
                                        arriveBuildingId=arriveBuildingId, needDetail=needDetail, planDate=planDate, remark=remark)

    """
        description：推荐记录数查询接口
        :Authorization:接口消息头中Authorization
        :union_id: 接口消息头中union_id
        :return:
    """
    @allure.step("APP接口-获取推荐记录数")
    def recommend_count_cmd(Authorization,union_id,brokerid):
        rec = recommend_count_cmd.Recommend_Count_Cmd(Authorization, union_id, brokerid)
        return rec.recommend_count_cmd()

class interface_user_manager:
    """
         description：APP登录注册等相关接口
    """
     #description：APP密码登录接口
     #phone:手机号
     #pwd: 密码
     #os_type: 验证码类型 	MiniApp(小程序),MiniWeb（公众号），Web,IOS,Android_App,Android,Android_Pad
     #app_version: app版本号
     #os_version: 系统版本号
     #hardware_version:硬件版本
     #app_uuid: 设备唯一ID
     #jpushId:极光推送的设备ID
     #lbsCityCode:LBS定位到的城市站点Code
     #siteCityCode:用户选择的城市站点Code
     #return:
    @allure.step("APP接口-密码登录")
    def app_login_pwd(self, phone=None, pwd=None, os_type=None, app_version=None, os_version=None,
                      hardware_version=None, app_uuid=None, jpushId=None, lbsCityCode=None, siteCityCode=None,
                      terminalType=None, loginSelection=None):
        rec = fcb_app_login_pwd_cmd.BrokerLonginPwd(terminalType=terminalType, loginSelection=loginSelection)
        out = rec.login_pwd_cmd(phone=phone, pwd=pwd, os_type=os_type, app_version=app_version, os_version=os_version,
                                hardware_version=hardware_version, app_uuid=app_uuid, jpushId=jpushId,
                                lbsCityCode=lbsCityCode, siteCityCode=siteCityCode)
        return out


class interface_member_center:
    """
    description：运营后台会员中心相关接口

    """
    #description：运营后台不同经纪人类型推荐上限查询接口
    #return:
    @allure.step("运营后台接口-获取推荐上限")
    def get_recommend_limit(self):
        rec = get_recommend_limit_cmd.GetRecommendLimitCmd()
        return rec.get_recommend_limit_cmd()

    #运营后台客户被推荐上限查询接口
    #return:
    @allure.step("运营后台接口-获取客户被推荐上限")
    def get_client_recommend_limit(self):
        rec = get_client_recommend_limit_cmd.GetClientRecommendLimitCmd()
        return rec.get_clinet_recommend_limit_cmd()

    # 运营后台推荐保护期查询接口
    #return:
    @allure.step("运营后台接口-获取推荐保护期天数")
    def get_recommend_unvisit_protect(self):
        rec = get_recommend_protectday_cmd.GetRecommendUnvisitCmd()
        return rec.get_recommend_unvisit_protect_cmd()

    # 运营后台到访保护期查询接口
    #return:
    @allure.step("运营后台接口-获取到访保护期天数")
    def get_recommend_visit_protect(self):
        rec = get_visit_protectday_cmd.GetRecommendVisitCmd()
        return rec.get_recommend_visit_protect_cmd()





