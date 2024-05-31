# -*- coding: utf-8 -*-
import time
import traceback
from FasterRunner.utils.logging import logger
from performApp.utils import error as err
from performApp import models
from performApp.utils.jmeterApi import JmRest
from performApp.utils.influxdbApi import InfluxDBofJmeter as Influx

state_columns = {
    'ok': {'avg': 'avg', 'pct90': 'pct90', 'pct95': 'pct95', 'pct99': 'pct99', 'tps': 'tps'},
    'ko': {'req_err_count': 'count'},
    'all': {'req_count': 'count'}
}


def get_influx_db_data(task_id):
    jmt = JmRest()
    task_detail = jmt.get_task_detail(task_id)
    scene_id = task_detail['sceneId']
    start_timestamp = int(time.mktime(time.strptime(task_detail['startTime'], "%Y-%m-%d %H:%M:%S"))) * 1000
    end_timestamp = int(time.mktime(time.strptime(task_detail['endTime'], "%Y-%m-%d %H:%M:%S")) + 1) * 1000

    task_result = Influx.get_application_data(task_id, start_timestamp, end_timestamp)
    logger.info('influxdb 数据：{}'.format(task_result))
    if not task_result:
        return
    period_time = end_timestamp - start_timestamp - 1000
    task_ret_dict = {}
    for seri in task_result['_raw']['series']:
        info = dict(zip(seri['columns'], seri['values'][0]))
        name = seri['tags']['transaction']
        state = seri['tags']['statut'] if seri['tags']['statut'] else 'ko'
        if name not in task_ret_dict:
            if name == 'all':
                task_ret_dict[name] = {k: info[v] * 100 for k, v in state_columns['ok'].items() if info.get(v)}
                task_ret_dict[name].update({'req_count': info['count'] * 100})
            else:
                task_ret_dict[name] = {k: info[v] * 100 for k, v in state_columns[state].items() if info.get(v)}
            task_ret_dict[name]['transaction'] = name
            task_ret_dict[name]['task_id'] = task_id
            task_ret_dict[name]['scene_id'] = scene_id
        else:
            task_ret_dict[name].update({k: info[v] * 100 for k, v in state_columns[state].items()
                                        if info.get(v)})

    task_ret_dict['all']['req_err_count'] = sum([data.get('req_err_count', 0)
                                                 for data in task_ret_dict.values()])
    for name, task in task_ret_dict.items():
        task_ret_dict[name]['tps'] = (task_ret_dict[name]['req_count'] -
                                      task_ret_dict[name].get('req_err_count', 0)) * 1000 // period_time
    return task_ret_dict.values()


def influxdb_run_task_data(task_id, flag=0):
    """
    运行场景任务的数据收集
    :param task_id:
    :param flag:
    :return:
    """
    try:
        jmt = JmRest()
        task_detail = jmt.get_task_detail(task_id)
        scene_id = task_detail['sceneId']
        scene_jconfig = jmt.get_jconfig_detail(scene_id)
        run_time = scene_jconfig['stressTime']
    except Exception as e:
        logger.error(traceback.format_exc())
        print(traceback.format_exc())
        raise
    retry = 0
    logger.info('查询运行后任务实时数据汇总')
    while retry < 3:
        retry += 1
        try:
            scene_detail = jmt.get_scene_detail(scene_id)
            if scene_detail['status'] == 1:
                time.sleep(int(run_time) if retry == 1 else 10)
                logger.info('场景还在运行中')
                continue
            elif scene_detail['status'] == 0:
                break
            logger.info('场景运行结束，收集运行任务数据')
            task_result_data = get_influx_db_data(task_id)
            obj_lst = [models.PerformJmeterData(**data, flag=flag) for data in task_result_data]
            if not models.PerformJmeterData.objects.filter(task_id=task_id).first():
                models.PerformJmeterData.objects.bulk_create(obj_lst)
            else:
                models.PerformJmeterData.objects.bulk_update(obj_lst)
            return list(task_result_data)
        except Exception as e:
            print(e)
            logger.error(str(traceback.format_exc()))
    return []


def run_task(uid, runner, times=1):
    task_lst = []
    jmt = JmRest()
    for _ in range(times):
        resp = jmt.run_scene(uid, runner)
        if not resp['data']:
            raise err.AppError(500, '压测任务执行失败')
        task_id = resp['data']
        logger.info('后端运行收集任务运行后数据......')
        influxdb_run_task_data(task_id)
        task_lst.append(resp['data'])
    return task_lst[0]


if __name__ == '__main__':
    def run_count(number):
        print(number)
        while number < 7:
            number += 1
            print(111111, number)
            if number > 8:
                break
        else:
            print('number:', number)


    run_count(1)
