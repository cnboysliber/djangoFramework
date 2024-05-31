

def response_msg(code, msg, success=True):
    return {
        "code": code,
        "success": success,
        "msg": msg
    }


SYSTEM_ERROR = response_msg("9999", "System Error", False)

API_ADD_SUCCESS = response_msg("0001", "接口添加成功", True)
API_UPDATE_SUCCESS = response_msg("0002", "API更新成功", True)
API_DEL_SUCCESS = response_msg("0003", "API删除成功", True)
API_NOT_FOUND = response_msg("0102", "未查询到该API", False)


PROJECT_ADD_SUCCESS = response_msg("0001", "项目添加成功")
PROJECT_UPDATE_SUCCESS = response_msg("0002", "项目更新成功")
PROJECT_DELETE_SUCCESS = response_msg("0003", "项目删除成功")
PROJECT_EXISTS = response_msg("0101", "项目已存在", False)
PROJECT_NOT_EXISTS = response_msg("0102", "项目不存在", False)

DEBUGTALK_NOT_EXISTS = response_msg("0001", "miss debugtalk", False)
DEBUGTALK_UPDATE_SUCCESS = response_msg("0002", "debugtalk更新成功")

TREE_ADD_SUCCESS = response_msg("0001", "树形结构添加成功")
TREE_UPDATE_SUCCESS = response_msg("0002", "树形结构更新成功")
TREE_NO_DATA = response_msg("0003", "树形结构无数据，请新建数据")


KEY_MISS = response_msg("0100", "请求数据非法", False)

FILE_UPLOAD_SUCCESS = response_msg("0001", "文件上传成功")
FILE_EXISTS = response_msg("0101", "文件已存在,默认使用已有文件", False)

YAPI_ADD_SUCCESS = response_msg("0001", "导入YAPI接口添加成功", True)
YAPI_ADD_FAILED = response_msg("0103", "导入YAPI接口失败", False)
YAPI_NOT_NEED_CREATE_OR_UPDATE=response_msg("0103", "YAPI无更新", False)

DATA_TO_LONG = response_msg("0100", "数据信息过长", False)

REPORT_DEL_SUCCESS = response_msg("0003", "测试报告删除成功", True)
REPORT_NOT_EXISTS = response_msg("0102", "指定的测试报告不存在", False)
REPORT_EXISTS = response_msg("0001", "测试报告存在", True)
REPORT_GET_SUCCESS = response_msg("0001", "获取测试报告成功", True)
REPORT_GET_FAILE = response_msg("0002", "获取测试报告失败", False)

SUITE_ADD_SUCCESS = response_msg("0001", "Suite添加成功", True)
SUITE_DEL_SUCCESS = response_msg("0003", "Suite删除成功", True)

CASE_ADD_SUCCESS = response_msg("0001", "用例添加成功", True)
CASE_SPILT_SUCCESS = response_msg("0001", "用例切割成功", True)
CASE_EXISTS = response_msg("0101", "此节点下已存在该用例集", False)
CASE_NOT_EXISTS = response_msg("0102", "此用例集不存在", False)
CASE_DELETE_SUCCESS = response_msg("0003", "用例集删除成功", True)
CASE_UPDATE_SUCCESS = response_msg("0002", "用例集更新成功", True)
CASE_STEP_SYNC_SUCCESS = response_msg("0002", "用例步骤同步成功", True)

CONFIG_EXISTS = response_msg("0101", "此配置已存在，请重新命名", False)
CONFIG_ADD_SUCCESS = response_msg("0001", "环境添加成功", True)
CONFIG_NOT_EXISTS = response_msg("0102", "指定的环境不存在", False)
CONFIG_MISSING = response_msg("0103", "缺少配置文件", False)
CONFIG_IS_USED = response_msg("0104", "配置文件被用例使用中,无法删除", False)
CONFIG_UPDATE_SUCCESS = response_msg("0002", "环境更新成功", True)

VARIABLES_ADD_SUCCESS = response_msg("0001", "变量添加成功", True)
VARIABLES_UPDATE_SUCCESS = response_msg("0002", "全局变量更新成功", True)
VARIABLES_EXISTS = response_msg("0101", "此变量已存在，请重新命名", False)
VARIABLES_NOT_EXISTS = response_msg("0102", "指定的全局变量不存在", False)

TASK_ADD_SUCCESS = response_msg("0001", "定时任务新增成功", True)
TASK_UPDATE_SUCCESS = response_msg("0002", "定时任务更新成功", True)
TASK_TIME_ILLEGAL = response_msg("0101", "时间表达式非法", False)
TASK_HAS_EXISTS = response_msg("0102", "定时任务已存在", False)
TASK_EMAIL_ILLEGAL = response_msg("0103", "请指定邮件接收人列表", False)
TASK_DEL_SUCCESS = response_msg("0003", "任务删除成功", True)
TASK_RUN_SUCCESS = response_msg("0001", "用例运行中，请稍后查看报告", True)

PLAN_DEL_SUCCESS = response_msg("0003", "集成计划删除成功", True)
PLAN_ADD_SUCCESS = response_msg("0001", "计划添加成功", True)
PLAN_KEY_EXIST = response_msg("0101", "该KEY值已存在，请修改KEY值", False)
PLAN_ILLEGAL = response_msg("0101", "提取字段格式错误，请检查", False)
PLAN_UPDATE_SUCCESS = response_msg("0002", "计划更新成功", True)


HOSTIP_EXISTS = response_msg("0101", "此域名已存在，请重新命名", False)
HOSTIP_ADD_SUCCESS = response_msg("0001", "域名添加成功", True)
HOSTIP_NOT_EXISTS = response_msg("0102", "指定的域名不存在", False)
HOSTIP_UPDATE_SUCCESS = response_msg("0002", "域名更新成功", True)
HOST_DEL_SUCCESS = response_msg("0003", "域名删除成功", True)

DBCONFIG_FAIL=response_msg("0004","添加数据库配置失败",False)
DBCONFIG_ADD_SUCCESS = response_msg("0001", "数据库配置添加成功", True)
DBCONFIG_NOT_EXISTS = response_msg("0102", "指定的数据库配置不存在", False)
DBCONFIG_UPDATE_SUCCESS = response_msg("0002", "数据库配置更新成功", True)
DBCONFIG_DEL_SUCCESS = response_msg("0003", "数据库配置删除成功", True)
DBCONFIG_EXISTS = response_msg("0101", "指定的数据库配置已存在", False)


ACCOUNT_FAIL=response_msg("0004","添加账号配置失败",False)
ACCOUNT_ADD_SUCCESS = response_msg("0001", "账号配置添加成功", True)
ACCOUNT_NOT_EXISTS = response_msg("0102", "指定的账号配置不存在", False)
ACCOUNT_UPDATE_SUCCESS = response_msg("0002", "账号配置更新成功", True)
ACCOUNT_DEL_SUCCESS = response_msg("0003", "账号配置删除成功", True)
ACCOUNT_EXISTS = response_msg("0101", "指定的账号配置已存在", False)


FIXTURE_FAIL=response_msg("0004","添加fixture失败",False)
FIXTURE_ADD_SUCCESS = response_msg("0001", "fixture添加成功", True)
FIXTURE_NOT_EXISTS = response_msg("0102", "指定的fixture不存在", False)
FIXTURE_UPDATE_SUCCESS = response_msg("0002", "fixture更新成功", True)
FIXTURE_DEL_SUCCESS = response_msg("0003", "fixture删除成功", True)
FIXTURE_EXISTS = response_msg("0101", "指定的fixture已存在", False)


EXCEL_UPLOAD_SUCCESS = response_msg("0001", "Excel上传成功", True)
EXCEL_UPLOAD_FAIL=response_msg("0004", "Excel上传失败", False)
EXCEL_UPLOAD_FORMAT_FAIL=response_msg("0005", "Excel上传失败，格式不正确", False)

EXCEL_IMPORT_SUCCESS = response_msg("0001", "Excel导入数据成功", True)
EXCEL_IMPORT_FAIL=response_msg("0004", "Excel导入数据失败", False)




