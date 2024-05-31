# -*- coding:utf-8 -*-


class AppError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '<%d %s>' % (self.code, self.message)


ErrNotLogin = AppError(110, '登陆异常')
ErrUserInvalid = AppError(599, '用户未授权')

ErrArgs = AppError(2000, '参数错误')
ErrInternal = AppError(2001, '服务内部错误')
ErrNotDept = AppError(2002, '部门不存在')
ErrNotPhone = AppError(2003, '手机资源不存在')
ErrCaseNameExist = AppError(2004, '用例名称已存在，请重命名')
ErrNotFindDept = AppError(2005, '项目接口暂不支持，请联络管理员添加')
ErrExistApply = AppError(2006, '当前时间段已有人使用或申请中')
ErrNotConnect = AppError(2007, '用例接口服务器异常')
ErrInternalRequest = AppError(2008, 'request请求异常')
ErrCaseNameNotExist = AppError(2009, '请先保存步骤')
ErrUnicodeEncodeError = AppError(2010, '请求值编码错误')
ErrInvalidJsonStr = AppError(2011, '接口参数JSON字符串异常，请仔细检查')
ErrStepUsedCase = AppError(2012, '接口关联了用例不可删除')
ErrRestUrlNotFind = AppError(2013, '项目环境未发现请求环境的服务地址')

ErrLogin = AppError(3001, '账号或密码错误')
ErrProjectNotFind = AppError(3002, '用户没有关联项目')
ErrNotDataForUpdate = AppError(3003, '更新的数据不存在')
ErrFESecondNotFind = AppError(3003, '你输入的二级通道费率有误！')
ErrFEFirstNotFind = AppError(3003, '你输入的一级通道费率有误！')
ErrFESumNotFind = AppError(3003, '你输入的总行费率有误！')
ErrFileType = AppError(3004, '错误的文件类型！')
ErrNotFindParam = AppError(3005, '参数%s不存在返回值中')
ErrNotFindFailedCase = AppError(3006, '该执行计划未发现失败的用例')
