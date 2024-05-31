from interface_runner.utils.response import *

ORGANIZATION_ADD_SUCCESS = response_msg("0001", "添加人员成功", True)
ORGANIZATION_DELETE_SUCCESS = response_msg("0002", "提测删除成功", True)
ORGANIZATION_UPLOAD_SUCCESS = response_msg("0003", "报告上传成功", True)
ORGANIZATION_TYPE_ERROR = response_msg("0004", "报告文件格式不对", False)
ORGANIZATION_UPDATE_SUCCESS = response_msg("0002", "人员更新成功", True)
ORGANIZATION_ADD_CONFIG_SUCCESS = response_msg("0001", "添加其他提测成功", True)
ORGANIZATION_UPDATE_CONFIG_SUCCESS = response_msg("0001", "更新其他提测成功", True)
ORGANIZATION_AUTH_PERMISSIONS = response_msg("0001", "暂无权限，请联系管理员", False)
ORGANIZATION_UPLOAD_ERROR = response_msg("0003", "报告上传失败", True)
# 月版本
MONTH_VERSION_ADD_SUCCESS = response_msg("0001", "添加成功", True)
MONTH_VERSION_UPDATE_SUCCESS = response_msg("0002", "更新成功", True)
MONTH_VERSION_DELETE_SUCCESS = response_msg("0003", "删除成功", True)
MONTH_VERSION_TIP_SUCCESS = response_msg("0004", "添加失败，月份已存在，请检查！", False)

VERSION_AUTH_PERMISSIONS = response_msg("0001", "暂无权限，请联系管理员", False)
# 系统月版本
VERSION_ADD_SUCCESS = response_msg("0001", "添加成功", True)
VERSION_UPDATE_SUCCESS = response_msg("0002", "更新成功", True)
VERSION_DELETE_SUCCESS = response_msg("0003", "删除成功", True)
# 每个系统版本
CHILD_VERSION_ADD_SUCCESS = response_msg("0001", "添加成功", True)
CHILD_VERSION_UPDATE_SUCCESS = response_msg("0002", "更新成功", True)
CHILD_VERSION_DELETE_SUCCESS = response_msg("0003", "删除成功", True)

