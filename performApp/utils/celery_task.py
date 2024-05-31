# -*- coding: utf-8 -*-
import json
import datetime
from FasterRunner.utils.celeryModel import celery_models

from FasterRunner.utils import format_json
from FasterRunner.utils import response
from FasterRunner.utils.logging import logger


class CeleryTask(object):
    """
    定时任务操作
    """
    TYPES = {
        1: "Interval",
        2: "crontab"
    }

    def __init__(self, **kwargs):
        logger.info("before process task data:\n {kwargs}".format(kwargs=format_json(kwargs)))
        self._name = kwargs.get("name")
        self._data = kwargs.get("data")
        self._schedule_time = kwargs.get("time")
        self._type = self.TYPES[int(kwargs.get('type'))]
        self._switch = kwargs.get("switch", True)
        self._kwargs = {
            "strategy": kwargs.get("strategy"),
            "mail_cc": kwargs.get("mail_cc"),
            "receiver": kwargs.get("receiver"),
            "type": self._type,
            "task_name": self._name,
            "time": self._schedule_time,
            "webhook": kwargs.get("webhook"),
            "updater": kwargs.get("updater"),
            "creator": kwargs.get("creator"),
        }
        self._format_time = None

    def get_schedule_obj(self):
        if self._type == 'crontab':
            return celery_models.CrontabSchedule.objects
        return celery_models.IntervalSchedule.objects

    def set_format_crontab(self, schedule_time, month=None, week=None,
                           day=None, hour=None, minute=None, date_format='%Y-%m-%d %H:%M'):
        """
        格式化时间
        """
        try:
            crontab_date = datetime.datetime.strptime(schedule_time, date_format)
        except Exception as e:
            logger.error(str(e))
            return response.TASK_TIME_ILLEGAL
        try:
            self._format_time = {
                'day_of_week': week or '*',
                'month_of_year': month or crontab_date.month,
                'day_of_month': day or crontab_date.day,
                'hour': hour or crontab_date.hour,
                'minute': minute or crontab_date.minute
            }
        except Exception as e:
            logger.warning(str(e))
            return response.TASK_TIME_ILLEGAL
        return response.TASK_ADD_SUCCESS

    def _format_interval(self, schedule_time):
        """
        格式化interval时间
        :return:
        """
        interval = schedule_time.split('|')
        if len(interval) != 2:
            return response.TASK_TIME_ILLEGAL

        try:
            self._format_time = {
                'every': interval[1],
                'period': interval[0],
            }
        except Exception as e:
            logger.warning(str(e))
            return response.TASK_TIME_ILLEGAL

        return response.TASK_ADD_SUCCESS

    def send_email_task(self):
        if self._kwargs["strategy"] == '始终发送' or self._kwargs["strategy"] == '仅失败发送':
            if self._kwargs["receiver"] == '':
                logger.debug('TODO send email')

    def add_task(self, task_module):
        """
        add crontab tasks
        """
        if celery_models.PeriodicTask.objects.filter(name__exact=self._name).count() > 0:
            logger.info("{name} tasks exist".format(name=self._name))
            return response.TASK_HAS_EXISTS

        self.send_email_task()

        # resp = self.format_time()
        # if not resp.get("success"):
        #     return resp

        objects = self.get_schedule_obj()

        task, created = celery_models.PeriodicTask.objects.get_or_create(name=self._name, task=task_module)
        schedule_obj = objects.filter(**self._format_time).first()
        if schedule_obj is None:
            schedule_obj = objects.create(**self._format_time)
        setattr(task, self._type, schedule_obj)
        task.enabled = self._switch
        task.args = json.dumps(self._data, ensure_ascii=False)
        task.kwargs = json.dumps(self._kwargs, ensure_ascii=False)
        task.save()
        logger.info("{name} {type} tasks save success".format(name=self._name, type=self._type))
        return response.TASK_ADD_SUCCESS

    def update_task(self, name):
        # resp = self.format_time()
        # if not resp["success"]:
        #     return resp

        task = celery_models.PeriodicTask.objects.get(name=name)
        objects = self.get_schedule_obj()
        schedule_obj = objects.filter(**self._format_time).first()
        if schedule_obj is None:
            schedule_obj = objects.create(**self._format_time)
        setattr(task, self._type, schedule_obj)
        task.enabled = self._switch
        task.args = json.dumps(self._data, ensure_ascii=False)
        task.kwargs = json.dumps(self._kwargs, ensure_ascii=False)
        task.name = self._name
        task.save()
        logger.info("{name} {type} tasks save success".format(name=self._name, type=self._type))
        return response.TASK_UPDATE_SUCCESS

    @staticmethod
    def stop_task(name):
        """
        暂时定时任务
        :param name:
        :return:
        """
        celery_models.PeriodicTask.objects.filter(name=name).update(enabled=False)
        return response.TASK_STOP_SUCCESS

    @staticmethod
    def del_task(name):
        """
        删除定时任务
        :param name:
        :return:
        """
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = False
        task.delete()
        return response.TASK_DEL_SUCCESS


