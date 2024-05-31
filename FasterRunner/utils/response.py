# -*- coding: utf-8 -*-


def response_msg(code, msg, success=True):
    return {
        "code": code,
        "success": success,
        "msg": msg
    }


SYSTEM_ERROR = response_msg("9999", "System Error", False)
UNAUTHORIZED_ERROR = response_msg("10000", "用户未授权操作", False)

TASK_ADD_SUCCESS = response_msg("0001", "定时任务新增成功", True)
TASK_UPDATE_SUCCESS = response_msg("0002", "定时任务更新成功", True)
TASK_DEL_SUCCESS = response_msg("0003", "任务删除成功", True)
TASK_RUN_SUCCESS = response_msg("0004", "任务启动成功", True)
TASK_STOP_SUCCESS = response_msg("0005", "定时任务停止", True)
TASK_TIME_ILLEGAL = response_msg("0101", "时间表达式非法", False)
TASK_HAS_EXISTS = response_msg("0102", "定时任务已存在", False)
TASK_EMAIL_ILLEGAL = response_msg("0103", "请指定邮件接收人列表", False)


