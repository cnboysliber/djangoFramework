# -*- coding: utf-8 -*-
import os

ConstNotActive = 0
ConstActive = 1
NOT_ACTIVE = 0
ACTIVE = 1

# 海外BU的部门ID
MiddleBUID = 1
BusinessBUID = 2
FinancialBUID = 4
BUAbroadID = 5

FreeEncryptName = '免签名加密'

ApplyingST = 0
AgreeST = 1
RejectedST = 2
CancelST = 3

applyCONST = {
    0: "申请中",
    1: "批准申请",
    2: "拒绝申请",
    3: "取消申请"
}

UnRunST = 0
WaitingST = 1
RunningST = 2
FailedST = 3
SuccessST = 4
TimeStatusCNT = {
    0: '未运行',
    1: '对列中',
    2: '运行中',
    3: '失败',
    4: '成功'
}
CaseOldVersion = 1
CaseNewVersion = 2
CaseNowVersion = 3
CaseVersionCNT = {
    1: '1.0版本',
    2: '2.0版本',
    3: '3.0版本'
}

HttpCNST = 1
InvokeCNST = 2
HessianCNST = 3
MysqlCNST = 4
OracleCNST = 5
UIWebCNST = 6
LinuxCmd = 7
RedisCmdCNST = 8
protocolList = [
    {'name': 'HTTP', 'key': 1},
    {'name': 'Dubbo(invoke)', 'key': 2},
    {'name': 'Dubbo(hessian)', 'key': 3},
    {'name': 'SQL(Mysql)', 'key': 4},
    {'name': 'SQL(Oracle)', 'key': 5},
    {'name': 'UIWeb', 'key': 6},
    {'name': 'LinuxCmd', 'key': 7},
    {'name': 'RedisCmd', 'key': 8},
]

DeptCnst = [
    {
        'workspaceId': 1,
        'name': '技术开发中心'
    }
]

TAPD_API_USER = 'xtlJ7T0O'
TAPD_API_KEY = 'A5038245-4288-8D04-2D9B-3C3EC1A77B4B'
SWIFT_ID = '20051781'
SWIFT_ABROAD_BU_ID = '39429000'
SWIFT_PROJECT_IDS = ['69487640', '41073022', '30146140']
TAPD_URL = 'https://api.tapd.cn/workspaces/projects?company_id={}'

YapiHost = 'http://yapi.ipd.swiftpass.cn/'

# 生产环境需要设置环境变量，开启UCC开关
# UCC_SWITCH = os.environ.get('UCC_SWITCH', None) == 'ON'
SERVER_ENV = os.environ.get('SERVER_ENV', 'develop')
UCC_SWITCH = SERVER_ENV in ['production', 'test']

if SERVER_ENV == 'test':
    ClientId = 'client-autoPlatformTest'
    Secret = '123456'
    UccHost = 'https://portal.swiftpass.cn'
# elif SERVER_ENV == 'production':
#     ClientId = 'client-autoPlatform'
#     Secret = 'auto200119'
#     UccHost = 'https://portal.swiftpass.cn'

elif SERVER_ENV == 'production':
    ClientId = 'client-autoPlatform1'
    Secret = '123456'
    UccHost = 'https://portal.swiftpass.cn'

ECC_PK = 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhfDkSOboJMlkwwBFN4whU19j' \
         '+1Mkwd+DXSijE/XYUb2MNbcUqijwWGAmBOhvhSMvm1q2ik9KClqa7bqcb2B5Yg=='

SendTOEmail = {'develop': ['李成波<chengbo.li@swiftpass.cn>', ],
               'production': ['李成波<chengbo.li@swiftpass.cn>',
                              '李立想<lixiang.li@swiftpass.cn>',
                              '於雷<lei.yu@swiftpass.cn>',
                              '周德国<deguo.zhou@swiftpass.cn>',
                              '李毅承<liyichen@hstypay.com>',
                              '张冰冰<bingbing.zhang@swiftpass.cn>',
                              '林珍(Jenny)<zhen.lin@swiftpass.cn>']
               }
