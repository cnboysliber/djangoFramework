import time
import os
import threading
import json

from loguru import logger
from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer, JsonWebsocketConsumer

from ..utils.common import get_terminal_task_log_path


class TaskLogWebsocket(AsyncJsonWebsocketConsumer):
    disconnected = False
    log_type = task_id = ''

    log_types = {
        'terminal': get_terminal_task_log_path,
    }

    async def connect(self):
        await self.accept()
        # user = self.scope["user"]
        # if user.is_authenticated:
        #     self.accept()
        # else:
        #     self.close()

    async def get_log_path(self, task_id):
        func = self.log_types.get(self.log_type)
        if func:
            return await func(task_id)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        data = json.loads(text_data)
        task_id = data.get('task')
        self.log_type = data.get('type', 'terminal')
        if task_id:
            self.handle_task(task_id)

    async def wait_util_log_path_exist(self, task_id):
        log_path = self.get_log_path(task_id)
        log_path = os.path.join(settings.BASE_DIR, 'logs\\debug.log')
        while not self.disconnected:
            if not os.path.exists(log_path):
                await self.send_json({'message': '.', 'task': task_id})
                time.sleep(0.5)
                continue
            await self.send_json({'message': '\r\n'})
            try:
                logger.debug('Task log path: {}'.format(log_path))
                task_log_f = open(log_path, 'rb')
                return task_log_f
            except OSError as e:
                return None

    async def read_log_file(self, task_id):
        task_log_f = self.wait_util_log_path_exist(task_id)
        if not task_log_f:
            logger.debug('Task log file is None: {}'.format(task_id))
            return

        task_end_mark = []
        while not self.disconnected:
            data = task_log_f.read(4096)
            if data:
                # data = data.replace(b'\n', b'\r\n')
                print(3333333333333, data.split(b'\r\n'))
                data = b'\r\n'.join([x.replace(b'%s::' % task_id.encode(), b'')
                                     for x in data.split(b'\r\n') if x.find(task_id.encode()) > -1])
                await self.send_json(
                    {'message': data.decode(errors='ignore'), 'task': task_id}
                )
                if data.find(task_id.encode()) != -1:
                    task_end_mark.append(1)
            elif len(task_end_mark) == 1:
                logger.debug('Task log end: {}'.format(task_id))
                break
            time.sleep(0.2)
        task_log_f.close()

    def handle_task(self, task_id):
        logger.info("Task id: {}".format(task_id))
        thread = threading.Thread(target=self.read_log_file, args=(task_id,))
        thread.start()

    async def disconnect(self, close_code):
        self.disconnected = True
        await self.close()
