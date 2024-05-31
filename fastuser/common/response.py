def response_msg(code, msg, success=True):
    return {
        "code": code,
        "success": success,
        "msg": msg
    }


SYSTEM_ERROR = response_msg("9999", "System Error", False)
KEY_MISS = response_msg("0100", "请求数据非法", False)

REGISTER_SUCCESS = response_msg("0001", "register success", True)
REGISTER_USERNAME_EXIST = response_msg("0101", "用户名已被注册", False)
REGISTER_EMAIL_EXIST = response_msg("0102", "邮箱已被注册", False)

LOGIN_SUCCESS = response_msg("0002", "login success", True)
LOGIN_FAILED = response_msg("0103", "用户名或密码错误", False)

USER_NOT_EXISTS = response_msg("0104", "该用户未注册", False)
USER_BLOCKED = response_msg("0105", "用户被禁用", False)

