from interface_runner.utils.response import *


PERFORM_ADD_SUCCESS = response_msg("0001", "添加提测成功", True)
PERFORM_DELETE_SUCCESS = response_msg("0002", "提测删除成功", True)
PERFORM_UPLOAD_SUCCESS = response_msg("0003", "报告上传成功", True)
PERFORM_TYPE_ERROR = response_msg("0004", "报告文件格式不对", False)
PERFORM_UPDATE_SUCCESS = response_msg("0002", "提测更新成功", True)
PERFORM_UPLOAD_EXE_ERROR = response_msg("0004", "解析jtl文件异常", False)
PERFORM_ADD_CONFIG_SUCCESS = response_msg("0001", "添加其他提测成功", True)
PERFORM_UPDATE_CONFIG_SUCCESS = response_msg("0001", "更新其他提测成功", True)
PERFORM_AUTH_PERMISSIONS = response_msg("0001", "暂无权限，请联系管理员", False)
PERFORM_UPLOAD_ERROR = response_msg("0003", "报告上传失败", True)
PROJECT_EXISTS_SUCCESS = response_msg("0001", "组件信息已存在", False)