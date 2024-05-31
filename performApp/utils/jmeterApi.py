# -*- coding:utf-8
from urllib.parse import urlparse
from django.conf import settings

from performApp.utils import error as err
from FasterRunner.utils.logging import logger
from FasterRunner.utils.baseRest import RestRequest


class JmRest(object):

    def __init__(self, host='http://qm.fcb.com.cn/'):
        self.req_success = 1
        self._host = host
        self._headers = {'Content-Type': 'application/json'}

    def add_scene(self, **kwargs):
        """
        新增场景
        :param kwargs:
        :return:
        """
        rest = RestRequest(self._host)
        rest.fetch('/stress/jscene/create', 'POST', headers=self._headers, **kwargs)
        if not rest.ok:
            logger.error(rest.data)
            raise
        return rest.data['data']

    def copy_scenes(self, body):
        """
        复制场景
        :param body:
        :param kwargs:
        :return:
         """
        data = {
            "sceneId": "S_12345678",
            "sceneName": "场景名称_copy"
        }
        # old_sceneId = body.get('sceneId'),  # 获取老场景ID
        # rest = RestRequest(self._host)
        # rest.fetch('/stress/jscene/create', 'POST', headers=self._headers, **kwargs)
        # if not rest.ok:
        #     logger.error(rest.data)
        #     raise
        # else:
        #     new_secenId = rest.data.sceneId  # 返回赋值新场景ID
        #     jc = self.get_jconfig_detail(old_sceneId)
        #     jc_body = {
        #         "sceneId": new_secenId,
        #         "numThreads": jc.data.get("numThreads"),
        #         "numNode": jc.data.get("numNode"),
        #         "stressTime": jc.data.get("stressTime"),
        #         "rameUp": jc.data.get("rameUp"),
        #         "isGlobal": jc.data.get("isGlobal"),
        #         "flowModel": jc.data.get("flowModel"),
        #     }
        #     rest.fetch('/stress/jconfig/add', 'POST', headers=self._headers, **jc_body, **kwargs)
        #     if not rest.ok or rest.data['result'] != self.req_success:
        #         logger.error(rest.data)
        #         raise
        #     else:
        #         pass
        return data

    def update_scene(self, body, **kwargs):
        """
        更新场景
        :param body:
        :param kwargs:
        :return:
        """
        data = {
            'sceneId': body.get('sceneId'),
            'sceneName': body.get('sceneName'),
            'updateBy': body.get('updateBy'),
            'remark': body.get('remark'),
        }
        rest = RestRequest(self._host)
        logger.info(data)
        rest.fetch('/stress/jscene/update', 'POST', headers=self._headers, **data, **kwargs)
        if not rest.ok:
            logger.error(rest.data)
            raise
        return rest.data

    def del_scene(self, scene_id, **kwargs):
        """
        删除场景
        :param scene_id:
        :param kwargs:
        :return:
        """
        logger.debug(kwargs)
        rest = RestRequest(self._host)
        rest.fetch('/stress/jscene/del/{sceneId}'.format(sceneId=scene_id), 'POST', headers=self._headers, **kwargs)
        if not rest.ok:
            logger.error(rest.data)
            raise
        return rest.data

    def get_scene_detail(self, scene_id, **kwargs):
        """
        查询单个场景
        :param scene_id:
        :param kwargs:
        :return:
        """
        # logger.debug(kwargs)
        rest = RestRequest(self._host)
        rest.fetch('/stress/jscene/get/{sceneId}'.format(sceneId=scene_id), 'POST', headers=self._headers, **kwargs)
        # logger.debug(rest.data)
        if not rest.ok:
            logger.error(rest.data)
            raise
        return rest.data['data']

    def get_scene_list(self, size=10, page=1, **kwargs):
        """
        查询场景列表
        :param size:
        :param page:
        :param kwargs:
        :return:
        """
        body = {
            'pageNum': page,
            'pageSize': size
        }
        rest = RestRequest(self._host)
        logger.debug(body)
        rest.fetch('/stress/jscene/list', 'POST', headers=self._headers, **body, **kwargs)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.error(rest.data)
            raise
        return rest.data['data']

    def get_script_list(self, body: dict = None, **kwargs):
        """
        查询脚本/参数化文件列表
        :param body:
        :param kwargs:
        :return:
        """
        if not body:
            body = {}
        data = {
            'pageNum': body.get('pageNumber', 1),
            'pageSize': body.get('pageSize', 10),
            'sceneId': body.get('sceneId', None),
        }
        rest = RestRequest(self._host)
        logger.debug(data)
        rest.fetch('/stress/jfile/list', 'POST', headers=self._headers, **data, **kwargs)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.error(rest.data)
            raise
        return rest.data['data']

    def del_script(self, body: dict = None, **kwargs):
        """
        删除脚本/参数化文件
        :param body:
        :param kwargs:
        :return:
        """
        if not body:
            body = {}
        rest = RestRequest(self._host)
        logger.debug(body)
        rest.fetch('/stress/jfile/del', 'POST', headers=self._headers, **body, **kwargs)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.error(rest.data)
            raise
        return rest.data

    def down_script(self, body: dict = None, **kwargs):
        """
        下载脚本/参数化文件
        :param body:
        :param kwargs:
        :return:
        """
        if not body:
            body = {}
        rest = RestRequest(self._host)
        sceneId = body.get('sceneId')
        name = body.get('name')
        logger.debug(body)
        rest.fetch(f'/stress/file/download/{sceneId}/{name}', 'GET', **kwargs)
        if not rest.ok:
            logger.error(rest.data)
            raise
        return rest.content

    def down_error_log(self, body: dict = None, **kwargs):
        """
        下载脚本/参数化文件
        :param body:
        :param kwargs:
        :return:
        """
        if not body:
            body = {}
        rest = RestRequest(self._host)
        sceneId = body.get('sceneId')
        taskId = body.get('taskId')
        logger.debug(body)
        rest.fetch(f'/stress/file/downloadError/{sceneId}/{taskId}', 'GET', **kwargs)
        if not rest.ok:
            logger.error(rest.data)
            raise
        return rest.content

    def upload_jmt_script(self, scene_id, file, **kwargs):
        """
        上传脚本文件
        :param scene_id:
        :param file:
        :param kwargs:
        :return:
        """
        headers = {}
        rest = RestRequest(self._host, False)
        rest.fetch('/stress/file/upload/{sceneId}'.format(sceneId=scene_id),
                   'POST', file=file, headers=headers, **kwargs)
        logger.debug(rest.data)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.error(rest.data)
            raise
        return rest.data

    def add_jconfig(self, body, **kwargs):
        """
        添加场景配置
        :param body: json
        {
            "sceneId": "",
            "numThreads": "",
            "numNode": "",
            "stressTime": "",
            "rameUp": "",
            "isGlobal": "",
            "flowModel": ""
        }
        :param kwargs:
        :return:
        """
        rest = RestRequest(self._host)
        logger.debug(body)
        rest.fetch('/stress/jconfig/add', 'POST', headers=self._headers, **body, **kwargs)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.error(rest.data)
            raise
        return rest.data

    def get_jconfig_detail(self, scene_id, **kwargs):
        """
        查询场景配置详情
        :param scene_id:
        :return:
        """
        rest = RestRequest(self._host)
        rest.fetch('/stress/jconfig/get/{sceneId}'.format(sceneId=scene_id),
                   'POST', headers=self._headers, **kwargs)
        logger.debug(rest.data)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.error(rest.data)
            raise
        return rest.data['data']

    def exist_jconfig(self, scene_id, **kwargs):
        """
                查询场景配置详情
                :param scene_id:
                :return:
                """
        rest = RestRequest(self._host)
        rest.fetch('/stress/jconfig/get/{sceneId}'.format(sceneId=scene_id),
                   'POST', headers=self._headers, **kwargs)
        logger.debug(rest.data)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.error(rest.data)
            raise
        return rest.data['data']

    def update_jconfig(self, body, **kwargs):
        """
        更新场景配置内容
        :param body:
        {
            "sceneId": "",
            "numThreads": "",
            "numNode": "",
            "stressTime": "",
            "rameUp": "",
            "isGlobal": "",
            "flowModel": ""
        }
        :param kwargs:
        :return:
        """
        rest = RestRequest(self._host)
        rest.fetch('/stress/jconfig/update',
                   'POST', headers=self._headers, **body, **kwargs)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.error(rest.data)
            raise
        return rest.data

    def run_scene(self, scene_id, runner, **kwargs):
        """
        运行场景
        :param scene_id:
        :param runner:
        :return:
        """
        data = {
            'runBy': runner
        }
        rest = RestRequest(self._host)
        rest.fetch('/stress/run/{sceneId}'.format(sceneId=scene_id),
                   'POST', headers=self._headers, **data, **kwargs)
        logger.debug(rest.data)
        if rest.data.get('status') == 500:
            raise err.AppError(500, rest.data['error'])
        elif not rest.ok or rest.data['result'] != self.req_success:
            logger.warning(rest.data)
            err_raise = err.ErrPerformRun
            err_raise.message = rest.data['msg']
            raise err_raise
        return rest.data

    def stop_scene(self, scene_id, **kwargs):
        """
        停止运行场景
        :param scene_id:
        :return:
        """
        rest = RestRequest(self._host)
        rest.fetch('/stress/stop/{sceneId}'.format(sceneId=scene_id),
                   'POST', headers=self._headers, **kwargs)
        logger.debug(rest.data)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.warning(rest.data)
            raise err.ErrPerformStop
        return rest.data['data']

    def get_work_list(self, **kwargs):
        """
        查询执行机
        :param kwargs:
        :return:
        """
        rest = RestRequest(self._host)
        rest.fetch('/stress/listWorks/', 'GET', headers=self._headers, **kwargs)
        logger.debug(rest.data)
        work_list = []
        for work_url, state in rest.data.items():
            url_ps = urlparse(work_url)
            host, port = url_ps.netloc.split(':')
            work_list.append({
                'host': host,
                'port': port,
                'state': state if state == '0' else '1',
                'service': work_url,
            })
        return work_list

    def get_jtask_list(self, body: dict = None, **kwargs):
        """
        查询任务列表
        :param body:
        :param kwargs:
        :return:
        """
        if not body:
            body = {}
        data = {
            'pageNum': body.get('pageNumber', 1),
            'pageSize': body.get('pageSize', 10),
            'sceneId': body.get('sceneId', None),
            'runBy': body.get('runBy', None),
            'flag': body.get('flag', None),
            'startTime': body.get('startTime', None),
        }
        rest = RestRequest(self._host)
        rest.fetch('/stress/jtask/list',
                   'POST', headers=self._headers, **data, **kwargs)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.warning(rest.data)
            raise err.ErrPerformStop
        return rest.data['data']

    def get_task_detail(self, task_id):
        """
        查询任务详情
        :param task_id:
        :return:
        """
        rest = RestRequest(self._host)
        rest.fetch('/stress/jtask/get/{taskId}'.format(taskId=task_id),
                   'POST', headers=self._headers,)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.warning(rest.data)
            raise err.ErrTaskQuery
        return rest.data['data']

    def task_remark(self, **data):
        """
        设置报告状态和备注
        :param data : {
            task_id:
            scene_id:
            remark:
            flag: 0: 普通报告， 1：最终报告
        }
        :return:
        """
        data['flag'] = int(data['flag'])
        rest = RestRequest(self._host)
        rest.fetch('/stress/jtask/remark',
                   'POST', headers=self._headers, **data)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.warning(rest.data)
            raise err.ErrReportRemark
        return rest.data['data']

    def work_action(self, worker, action):
        """
        重启/下线worker服务
        :param worker:
        :param action: restart, shutdown
        :return:
        """
        body = {
            'worker': worker
        }
        logger.debug(body)
        rest = RestRequest(self._host, False)
        logger.debug(f'正在{action}压测机器 {worker}...')
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        rest.fetch(f'/stress/{action}',
                   'POST', headers=headers, **body)
        logger.debug(rest.data)
        if not rest.ok or rest.data['result'] != self.req_success:
            logger.warning(rest.data)
            raise err.ErrTaskQuery


if __name__ == '__main__':
    jmt = JmRest('http://10.101.42.80:8070/')

    resp_data = jmt.down_script({'sceneId': 'S_GWkkcpGJ','name': 'test.jmx'})
    import json
    print(resp_data)







