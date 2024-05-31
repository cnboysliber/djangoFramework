# -*- coding:utf-8 -*-
import os
import time
import random

from performApp.utils.influxdbApi import InfluxDBofJmeter as Influx
from performApp.utils.jmeterApi import JmRest
from performApp import models
from FasterRunner.utils.logging import logger


def get_terminal_task_log_path(task_id):
    pass


def get_user_info(request):  # add接口加入用户信息
    data = request.data
    _mutable = data._mutable
    data._mutable = True
    data['creator'] = request.user.username
    data['updater'] = request.user.username
    data._mutable = _mutable
    return request


# weight_data 的数据类型为 dict
def random_weight(weight_data):
    total = sum(weight_data.values())    # 权重求和
    ra = random.uniform(0, total)   # 在0与权重和之前获取一个随机数
    curr_sum = 0
    ret = None
    keys = weight_data.keys()        # 使用Python3.x中的keys
    for k in keys:
        curr_sum += weight_data[k]             # 在遍历中，累加当前权重值
        if ra <= curr_sum:          # 当随机数<=当前权重和时，返回权重key
            ret = k
            break
    return ret


def random_select(data, n):
    src_data = {k: v for k, v in data.items()}
    results = []
    i = 0
    while i < n:
        m = random_weight(src_data)
        if m in results:
            continue
        results.append(m)
        src_data.pop(m)
        i = i+1
    return results


def push_perform_data(scene_id, task_id):
    """
    :param scene_id:
    :param task_id:
    :return:
    """
    jmt = JmRest()
    scene = jmt.get_jconfig_detail(scene_id)
    run_time = scene['stressTime']
    time.sleep(run_time + 10)
    now = int(time.time() * 1000)
    before_day = now - 60 * 60 * 10 * 1000  # 10小时前毫秒
    influx_data = Influx.get_application_data(task_id, before_day, now)
    if not influx_data:
        logger.error('压测异常，未查到数据')
        raise

    series = influx_data['_raw']['series']



