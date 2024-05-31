import jinja2

gather_str = """
import time
import platform
from _pytest import terminal
from interface_runner import models


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    '''收集测试结果'''
    # print(terminalreporter.stats)
    total = terminalreporter._numcollected
    passed = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    failed = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    error = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    skipped = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    successful = len(terminalreporter.stats.get('passed', [])) / terminalreporter._numcollected * 100
    # terminalreporter._sessionstarttime 会话开始时间
    duration = time.time() - terminalreporter._sessionstarttime
    # print('total times: %.2f' % duration, 'seconds')

    result = {
        "success": True,
        "stat": {
            "testsRun": total,
            "failures": failed,
            "errors": error,
            "skipped": skipped,
            "expectedFailures": 0,
            "unexpectedSuccesses": 0,
            "successes": passed
        },
        "time": {
            "start_at": terminalreporter._sessionstarttime,
            "duration": duration
        },
        "platform": {
            "fcb_runner": 1.0,
            "python_version": "{} {}".format(
                platform.python_implementation(), platform.python_version()
            ),
            "platform": platform.platform(),
        }
    }

    if total == passed:
        result["success"] = True
        status = 1
    else:
        result["success"] = False
        status = 0
    models.Report.objects.create(**{
        "project": models.Project.objects.get(name="{{project_name}}"),
        "name": "{{report_name}}",
        "type": {{report_type}},
        "status": status,
        "summary": result,
        "creator": "{{user}}",
        "env_id":{{env_id}},
    })"""
