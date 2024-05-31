from FasterRunner.utils.baseError import AppError

ErrArgs = AppError(301000, '参数错误')
ErrTokenFail = AppError(301001, '登录令牌失效')
ErrUserUnregistered = AppError(301002, '用户未注册')

ErrInternal = AppError(302000, '服务器内部错误')
ErrOperation = AppError(302001, '操作失败')
ErrInternalRequest = AppError(302002, '内部请求错误')

ErrTargetNoMatch = AppError(303000, '没有匹配的salt target')
ErrSaltCmdRetEmpty = AppError(303001, 'SALT执行结果返回为空')
ErrSaltMasterNotResponding = AppError(303002, 'SALT Master没有响应')
ErrPerformSrvLack = AppError(304000, '执行机数量不足')

ErrPerformRunning = AppError(305000, '场景正在运行中')
ErrPerformStop = AppError(305100, '场景停止失败')
ErrPerformRun = AppError(305101, '场景运行失败')
ErrTaskQuery = AppError(305200, '场景详情查询错误')
ErrWorkStop = AppError(305201, '节点服务停止失败')
ErrWorkRestart = AppError(305202, '节点服务重启失败')
ErrReportRemark = AppError(305203, '任务报告备注异常')
