from datetime import datetime
from celery import shared_task

from performApp import models
from FasterRunner.utils.logging import logger
from FasterRunner.threadpool import execute
from performApp.utils.jmeterApi import JmRest
from performApp.utils.exeTask import influxdb_run_task_data


@shared_task
def scene_task(scene_uid, *args, **kwargs):
    """
    定时任务测试
    :param scene_uid:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        runner = 'admin'
        jmt = JmRest()
        logger.info('定时自动运行开始......')
        scene = models.ScenesManage.objects.get(scene_uid=scene_uid, status=1)
        scene_plan = models.ApiPerformancePlan.objects.get(scene_id=scene.id, status=1)
        if scene_plan.plan_type == 1:
            task_time = kwargs.get('time')
            run_day_of_week = [int(d) for d in task_time.split('|')[0].split(',')]
            now_day_of_week = datetime.now().weekday() + 1
            if now_day_of_week not in run_day_of_week:
                logger.info('定时任务当前不需要运行：{} ,周期时间: {}'
                            .format(datetime.now().strftime('%Y-%m-%d %H:%M'), task_time))
                return

        ret = jmt.run_scene(scene_uid, runner)
        influxdb_run_task_data(ret['data'])

    except Exception as e:
        logger.error('定时场景任务运行异常:{}'.format(e))
    finally:
        logger.info('定时自动运行结束......')



