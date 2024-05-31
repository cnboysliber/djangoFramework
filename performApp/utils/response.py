from FasterRunner.utils.response import *


PERFORM_ADD_SUCCESS = response_msg("0001", "添加报告成功", True)
PERFORM_DELETE_SUCCESS = response_msg("0002", "报告删除成功", True)
PERFORM_UPLOAD_SUCCESS = response_msg("0003", "报告上传成功", True)
PERFORM_TYPE_ERROR = response_msg("0004", "报告文件格式不对", False)
PERFORM_UPDATE_SUCCESS = response_msg("0005", "报告更新成功", True)
PERFORM_UPLOAD_EXE_ERROR = response_msg("0006", "解析jtl文件异常", False)
PERFORM_UPLOAD_ERROR = response_msg("0007", "报告上传失败", False)
PERFORM_REPORT_EMPTY = response_msg("0008", "报告为空, 请检查是否上传", False)
PERFORM_REPORT_EXIST = response_msg("0008", "报告已上传", True)
# 测试类型
TYPE_ADD_SUCCESS = response_msg("0101", "添加成功", True)
TYPE_DELETE_SUCCESS = response_msg("0102", "删除成功", True)
TYPE_UPDATE_SUCCESS = response_msg("0103", "更新成功", True)
TYPE_DELETE_ERROR = response_msg("0104", "类型已引用不可删除", True)

# 代码覆盖率收集
COVERAGE_RUN_SUCCESS = response_msg("0200", "覆盖率运行成功", True)
COVERAGE_RUN_ERROR = response_msg("0201", "覆盖率运行失败", False)

# 项目管理
PROJECT_ADD_SUCCESS = response_msg("0301", "添加成功", True)
PROJECT_DELETE_SUCCESS = response_msg("0302", "删除成功", True)
PROJECT_UPDATE_SUCCESS = response_msg("0303", "更新成功", True)
NULL_TIP_INFO = response_msg("0304", "项目为空，请创建项目", True)

# 环境管理
ENV_ADD_SUCCESS = response_msg("0401", "添加成功", True)
ENV_DELETE_SUCCESS = response_msg("0402", "删除成功", True)
ENV_UPDATE_SUCCESS = response_msg("0403", "更新成功", True)

# 压力机管理
PRESS_ADD_SUCCESS = response_msg("0501", "添加成功", True)
PRESS_DELETE_SUCCESS = response_msg("0502", "删除成功", True)
PRESS_UPDATE_SUCCESS = response_msg("0503", "更新成功", True)
PERFORM_SERVER_ADD_SUCCESS = response_msg("0501", "添加成功", True)
PERFORM_SERVER_DELETE_SUCCESS = response_msg("0502", "删除成功", True)
PERFORM_SERVER_UPDATE_SUCCESS = response_msg("0503", "更新成功", True)

# 场景管理
SCENES_ADD_SUCCESS = response_msg("0601", "添加成功", True)
SCENES_DELETE_SUCCESS = response_msg("0602", "删除成功", True)
SCENES_UPDATE_SUCCESS = response_msg("0603", "更新成功", True)
SCENES_CONFIG_ADD_SUCCESS = response_msg("0604", "场景配置添加成功", True)
SCENES_CONFIG_UPDATE_SUCCESS = response_msg("0604", "场景配置更新成功", True)
SCENES_RUN_SUCCESS = response_msg("0605", "场景运行成功", True)
SCENES_STOP_SUCCESS = response_msg("0606", "场景停止成功", True)

# BUG管理
BUGS_ADD_SUCCESS = response_msg("0701", "添加成功", True)
BUGS_DELETE_SUCCESS = response_msg("0702", "删除成功", True)
BUGS_UPDATE_SUCCESS = response_msg("0703", "更新成功", True)
BUGS_UPLOAD_SUCCESS = response_msg("0704", "上传成功", True)
BUGS_UPLOAD_ERROR = response_msg("0705", "上传失败", True)
BUGS_UPDATE_ERROR = response_msg("0705", "上传失败", True)

# 复制场景
SCENES_COPY_SUCCESS = response_msg("0801", "场景复制成功", True)
SCENES_COPY__ERROR = response_msg("0802", "场景复制失败", True)

# 压测节点管理
WORKER_RESTART_SUCCESS = response_msg("0901", "节点重启成功", True)
WORKER_STOP_SUCCESS = response_msg("0901", "节点停止成功", True)

# 任务管理
REMARK_TASK_SUCCESS = response_msg("1001", "任务报告备注成功", True)

