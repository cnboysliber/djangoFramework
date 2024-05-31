# -*- coding: utf-8 -*-

import os
import uuid
import time
import hashlib
import traceback

import performApp.utils.error

try:
    pass
    import fcntl
    import salt.client
    from salt.exceptions import SaltClientError
except Exception as e:
    print(e)

from FasterRunner.utils.logging import logger
from FasterRunner.utils import baseError as err
from FasterRunner.utils.baseRest import RestRequest


def with_file_lock(func):
    def wrapper(*args, **kwargs):
        with open('.timer.lock', 'w') as fl:
            try:
                fcntl.flock(fl, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError as e:
                if e.errno == 11:
                    return
            func(*args, **kwargs)

            fcntl.flock(fl, fcntl.LOCK_UN)

    return wrapper


def with_file_lock_build(func):
    def wrapper(*args, **kwargs):
        with open('.timer.lock.build', 'w') as fl:
            try:
                fcntl.flock(fl, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError as e:
                if e.errno == 11:
                    return
            func(*args, **kwargs)

            fcntl.flock(fl, fcntl.LOCK_UN)

    return wrapper


class SaltCmd(object):

    def salt_mk_md5(self, target, filepath):
        cmd = 'ret=$(md5sum {}) && echo $ret "\nok"'.format(filepath)
        return self._salt_cmd(target, cmd)

    @staticmethod
    def calc_md5(self, filepath):
        with open(filepath, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            return md5obj.hexdigest()

    @staticmethod
    def _salt_set_mode(target, file_path, mode='0755'):
        logger.info('<salt command - set mode> <%s>' % file_path)

        try:
            client = salt.client.LocalClient()
            ret = client.cmd(target, 'file.set_mode', [file_path, mode])
            if ret[target] is False:
                return -1, 'fail to set file mode to %s' % mode

            if len(ret[target]) > 0 and ret[target] == mode:
                return 0, ret[target].encode('utf-8')
        except SaltClientError:
            logger.error(traceback.format_exc())
            raise performApp.utils.error.ErrSaltMasterNotResponding
        except KeyError:
            return -1, str(performApp.utils.error.ErrTargetNoMatch)
        except Exception as e:
            logger.error(traceback.format_exc())
            return -1, str(e)

        if len(ret[target]) == 0:
            return -1, performApp.utils.error.ErrSaltCmdRetEmpty

        return -1, ret[target].encode('utf-8')

    @staticmethod
    def _salt_cp_file(target, source, dest, cp_type='cp.get_file'):
        logger.info('<salt command - copy %s> <%s> <%s>' % (cp_type, source, dest))

        try:
            cmd = ['salt://' + source, dest]
            logger.info('salt cmd: %s' % cmd)

            client = salt.client.LocalClient()

            ret = client.cmd(target, cp_type, cmd, timeout=180)
            if ret[target] is False:
                return -1, 'fail to copy file'

            if len(ret[target]) > 0 and ret[target] == dest:
                return 0, ret[target].encode('utf-8')
        except SaltClientError:
            logger.error(traceback.format_exc())
            raise performApp.utils.error.ErrSaltMasterNotResponding
        except KeyError:
            return -1, str(performApp.utils.error.ErrTargetNoMatch)
        except Exception as e:
            logger.error(traceback.format_exc())
            return -1, str(e)

        if len(ret[target]) == 0:
            return -1, performApp.utils.error.ErrSaltCmdRetEmpty

        return -1, ret[target].encode('utf-8')

    @staticmethod
    def _salt_cmd(target, cmd, timeout=180):
        print('salt "{0}" cmd.run "{1}"'.format(target, cmd))
        logger.info('salt "{0}" cmd.run "{1}"'.format(target, cmd))

        try:
            client = salt.client.LocalClient()

            ret = client.cmd(target, 'cmd.run', [cmd, 'shell="/bin/bash"',
                                                 'runas="root"'], timeout=timeout)
            if ret[target] is False:
                return -1, 'fail to execute command'

            if len(ret[target]) > 0 and ret[target][-3:] == '\nok':
                return 0, ret[target].encode('utf-8')
        except SaltClientError:
            print(traceback.format_exc())
            logger.error(traceback.format_exc())
            raise performApp.utils.error.ErrSaltMasterNotResponding
        except KeyError:
            return -1, str(performApp.utils.error.ErrTargetNoMatch)
        except Exception as e:
            print(traceback.format_exc())
            logger.error(traceback.format_exc())
            return -1, str(e)

        if len(ret[target]) == 0:
            return -1, performApp.utils.error.ErrSaltCmdRetEmpty

        return -1, ret[target].encode('utf-8')

    def clean_dist_path(self, target, dist_path):
        cmd = 'rm -rf {0} && mkdir -p {0} && echo "\nok"'.format(dist_path)
        has_err, rv = self._salt_cmd(target, cmd)
        return has_err, rv

    def check_path(self, target, app_path):
        cmd = 'if [ ! -d "%s" ]; then echo 1; else echo "\nok"; fi' % app_path

        return self._salt_cmd(target, cmd)

    def check_file(self, target, app_path, app_name):
        cmd = 'cd {0} && if [ ! -f "{1}" ]; then echo 1; else echo "\nok"; fi' \
            .format(app_path, app_name)

        return self._salt_cmd(target, cmd)

    def fetch_config_file_name(self, target, path, app_name, tag):
        cmd = 'cd {0} && ls | grep -w *.{1}.{2}; echo "\nok"' \
            .format(path, app_name, tag)

        return self._salt_cmd(target, cmd)

    def bake_config_file(self, target, config_path, file_name, real_name, app_name, tag):
        cmd = 'cd {0} && cp {1} {2}.{3}.{4} && echo "\nok"' \
            .format(config_path, file_name, real_name, app_name, tag)

        return self._salt_cmd(target, cmd)

    def bake_front_deploy_path(self, target, deploy_path):
        cmd = 'mv {0} {0}.bak'.format(deploy_path)
        return self._salt_cmd(target, cmd)

    def check_branch_exsit(self, target, repo_path, branch_name):
        cmd = 'cd {0} && branch=$(git branch | grep -w {1}$); ' \
              'if [ ! -n "$branch" ]; then echo 1; else echo "\nok"; fi' \
            .format(repo_path, branch_name)

        return self._salt_cmd(target, cmd)

    def check_process_exsit(self, target, process_name):
        cmd = 'cd / && process=$(ps aux | grep -w {} | grep -v grep); ' \
              'if [ ! -n "$process" ]; then echo 1; else echo "\nok"; fi' \
            .format(process_name)

        return self._salt_cmd(target, cmd)

    def checkout_tag(self, target, path, tag):
        not_exsit, _ = self.check_branch_exsit(target, path, tag)
        if not_exsit:
            cmd = 'cd {0} && git reset --hard && git clean -f && ' \
                  'git fetch origin refs/tags/{1} && ' \
                  'git fetch origin && git branch {1} {1} && ' \
                  'git checkout {1} && echo "\nok"'.format(path, tag)
        else:
            cmd = 'cd {0} && git reset --hard && git clean -f && ' \
                  'git checkout {1} && echo "\nok"'.format(path, tag)

        return self._salt_cmd(target, cmd)

    def clone_repo(self, target, repo, app_path):
        cmd = 'git clone {0} {1} && echo "\nok"'.format(repo, app_path)

        return self._salt_cmd(target, cmd)

    def salt_exec_hook(self, target, app_path, hook_cmd):
        if hook_cmd is None or hook_cmd == '':
            hook_cmd = 'echo "\nok"'

        cmd = 'cd {0} && ({1}) && echo "\nok"'.format(app_path, hook_cmd)

        return self._salt_cmd(target, cmd)

    def salt_start_app(self, target, app_path, start_cmd):
        if start_cmd is None or start_cmd == '':
            start_cmd = 'echo "\nok"'

        cmd = 'cd {0} && ({1}) && echo "\nok"'.format(app_path, start_cmd)

        return self._salt_cmd(target, cmd)

    def salt_restart_app(self, target, app_path, restart_cmd):
        if restart_cmd is None or restart_cmd == '':
            restart_cmd = 'echo "\nok"'

        cmd = 'cd {0} && ({1}) && echo "\nok"'.format(app_path, restart_cmd)

        return self._salt_cmd(target, cmd)

    def salt_stop_app(self, target, app_path, stop_cmd):
        if stop_cmd is None or stop_cmd == '':
            stop_cmd = 'echo "\nok"'

        cmd = 'cd {0} && ({1}) && echo "\nok"'.format(app_path, stop_cmd)

        return self._salt_cmd(target, cmd)

    def salt_build(self, target, build_path, build_cmd):
        if build_cmd is None or build_cmd == '':
            build_cmd = 'echo "\nok"'

        cmd = 'cd {0} && mkdir -p bin && {1} && echo "\nok"'.format(build_path,
                                                                    build_cmd)

        return self._salt_cmd(target, cmd)

    def salt_thrift_build(self, target, build_path, build_cmd):
        cmd = 'cd {0} && {1} && echo "\nok"'.format(build_path, build_cmd)

        return self._salt_cmd(target, cmd)

    def salt_build_apk(self, target, build_path, build_cmd):
        if build_cmd is None or build_cmd == '':
            build_cmd = 'echo "\nok"'

        cmd = 'cd {0} && {1} && echo "\nok"'.format(build_path, build_cmd)

        return self._salt_cmd(target, cmd, timeout=3000)

    def salt_build_front(self, target, build_path, build_cmd):
        """
        前端编译
        :param target:
        :param build_path:
        :param build_cmd:
        :return:
        """
        cmd = 'cd {0} && sh {1} > build.log && echo "\nok"'.format(build_path, build_cmd)

        return self._salt_cmd(target, cmd)

    def salt_check_apk(self, target, build_path):
        check_cmd = 'exist=$(ls {0} | grep .apk); ' \
                    'if [ ! -n "$exist" ]; then echo 1; else echo $exist"\nok"; fi'.format(build_path)
        return self._salt_cmd(target, check_cmd)

    def salt_push_apk(self, target, cmd):
        return self._salt_cmd(target, cmd)

    def scan_path_files(self, target, deploy_path, dest_path):
        """
        遍历目录里的所有文件
        :param target:
        :param deploy_path:
        :param dest_path:
        :return:
        """
        bash_path = os.path.join(deploy_path, 'scan_publish_files.sh')

        cmd = 'sh {0} {1} && echo "\nok"'.format(bash_path, dest_path)
        has_err, rv = self._salt_cmd(target, cmd)

        return has_err, rv

    def copy_app_bin(self, target, app_deploy_path, app_path):
        has_err, rv = self._salt_cp_file(target, app_deploy_path, app_path)
        if has_err:
            return has_err, rv
        else:
            return self._salt_set_mode(target, app_path)

    def copy_file(self, target, source, dest):
        return self._salt_cp_file(target, source, dest)

    def copy_dir(self, target, source, dest):
        return self._salt_cp_file(target, source, dest, 'cp.get_dir')

    def make_directory(self, target, path):
        cmd = 'mkdir -p {} && echo "\nok"'.format(path)

        return self._salt_cmd(target, cmd)

    @staticmethod
    def allowed_zip_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'zip'}

    @staticmethod
    def allowed_xml_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'xml'}

    @staticmethod
    def generate_uid(prefix=''):
        s = str(time.time())[1:6] + uuid.uuid4().hex[:6]
        if prefix:
            return prefix + '-' + s

        return s


class SaltApi(object):

    def __init__(self, host='http://10.101.42.80:9001', username='saltmaster', password='salt@123456', **kwargs):
        # 设置超时时间
        self.timeout = kwargs.get("timeout", 300)
        # 获取url
        self._host = host
        self._username = username
        self._password = password
        self._token_id = self.get_token()

    # token id 获取
    def get_token(self):
        request = RestRequest(self._host)
        obj = {'eauth': 'pam', 'username': self._username, 'password': self._password}
        request.fetch(uri="/login", method='POST', **obj)
        if request.data:
            try:
                self._token_id = request.data['return'][0]['token']
            except KeyError:
                raise KeyError
        return self._token_id

    def post(self, **kwargs):
        request = RestRequest(self._host)
        headers = {'X-Auth-Token': self._token_id, 'Content-Type': 'application/json'}
        request.fetch(uri="/", method='POST', headers=headers, **kwargs)
        if request.status_code != 200:
            raise performApp.utils.error.ErrInternalRequest
        return request.data

    def all_key(self):
        """
        获取所有的minion_key
        """
        obj = {'client': 'wheel', 'fun': 'key.list_all'}
        content = self.post(**obj)
        logger.info(content)
        # 取出认证已经通过的
        minions = content['return'][0]['data']['return']['minions']
        # 取出未通过认证的
        minions_pre = content['return'][0]['data']['return']['minions_pre']
        # print('未认证',minions_pre)
        return minions, minions_pre

    def accept_key(self, node_name):
        """
        如果你想认证某个主机 那么调用此方法
        """
        obj = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        content = self.post(**obj)
        ret = content['return'][0]['data']['success']
        return ret

    # 删除认证方法
    def delete_key(self, node_name):
        obj = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}

        content = self.post(**obj)

        ret = content['return'][0]['data']['success']
        return ret

    def host_remote_async_func(self, tgt, fun, arg):
        """
        远程异步执行
        :return:local_async
        """
        """
                执行fun 传入传入参数arg
                :param tgt:
                :param fun:
                :param arg:
                :return:
                """
        obj = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg}

        content = self.post(**obj)
        if content.get('return'):
            return content['return'][0]
        return content

    def host_remote_cmd_run(self, tgt, cmd):
        """
        执行cmd方法
        :param tgt:
        :param cmd:
        :return:
        """
        return self.host_remote_execution_module(tgt, 'cmd.run', cmd)

    # 针对主机远程执行模块
    def host_remote_func(self, tgt, fun):
        """ tgt是主机 fun是模块
            写上模块名 返回 可以用来调用基本的资产
            例如 curl -k https://ip地址:8080/ \
        >      -H "Accept: application/x-yaml" \
        >      -H "X-Auth-Token:b50e90485615309de0d83132cece2906f6193e43" \
        >      -d client='local' \
        >      -d tgt='*' \
        >      -d fun='test.ping'  要执行的模块
        return:
        - iZ28r91y66hZ: true
          node2.minion: true
        """
        obj = {'client': 'local', 'tgt': tgt, 'fun': fun}

        content = self.post(**obj)
        ret = content['return'][0]
        return ret

    def group_remote_func(self, tgt, fun):
        obj = {'client': 'local', 'tgt': tgt, 'fun': fun, 'expr_form': 'nodegroup'}

        content = self.post(**obj)
        ret = content['return'][0]
        return ret

    def host_remote_execution_module(self, tgt, fun, arg):
        """
        执行fun 传入传入参数arg
        :param tgt:
        :param fun:
        :param arg:
        :return:
        """
        obj = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg}

        content = self.post(**obj)
        logger.info(content)
        if content.get('return'):
            return content['return'][0]
        return content

    def host_push_file(self, tgt, arg, sync=True):
        """
        往master上推文件
        :param tgt:
        :param arg:
        :param sync:
        :return:
        """
        client = 'local' if sync else 'local_async'
        obj = {'client': client, 'tgt': tgt,
               'fun': 'cp.push',
               'arg': arg}

        content = self.post(**obj)
        if content.get('return'):
            return content['return'][0]
        return content

    def host_cp_file(self, tgt, source_path, dest_path, *args, sync=True):
        """
        文件复制
        :param tgt:
        :param source_path:
        :param dest_path:
        :param sync: 是否同步运行
        :param args: 可以添加其他参数
        :return:
        """
        client = 'local' if sync else 'local_async'
        obj = {'client': client, 'tgt': tgt,
               'fun': 'cp.get_file',
               'arg': ['salt://' + source_path, dest_path, 'makedirs=true', *args]}

        content = self.post(**obj)
        logger.info(content)
        if content.get('return'):
            return content['return'][0]
        return content

    def group_remote_execution_module(self, tgt, fun, arg):
        """
        根据分组来执行
        tgt =
        """

        obj = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'nodegroup'}

        content = self.post(**obj)
        jid = content['return'][0]
        return jid

    def host_sls(self, tgt, arg):
        """主机进行sls"""
        obj = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}

        content = self.post(**obj)
        return content

    def group_sls(self, tgt, arg):
        """ 分组进行sls """
        obj = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': 'nodegroup'}

        content = self.post(**obj)
        jid = content['return'][0]['jid']
        return jid

    def host_sls_async(self, tgt, arg):
        """主机异步sls """
        obj = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}

        content = self.post(**obj)
        jid = content['return'][0]['jid']
        return jid

    def group_sls_async(self, tgt, arg):
        """分组异步sls """
        obj = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': 'nodegroup'}

        content = self.post(**obj)
        jid = content['return'][0]['jid']
        return jid

    def server_group_pillar(self, tgt, arg, **kwargs):
        """分组进行sls and pillar"""
        obj = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': 'nodegroup',
               'kwarg': kwargs}

        content = self.post(**obj)
        jid = content['return'][0]
        return jid

    def server_hosts_pillar(self, tgt, arg, **kwargs):
        """针对主机执行sls and pillar """
        obj = {"client": "local", "tgt": tgt, "fun": "state.sls", "arg": arg, "kwarg": kwargs}

        content = self.post(**obj)
        jid = content['return'][0]
        return jid

    def jobs_all_list(self):
        """打印所有jid缓存"""

        obj = {"client": "runner", "fun": "jobs.list_jobs"}
        content = self.post(**obj)
        return content

    def jobs_jid_status(self, jid):
        """查看jid运行状态"""

        obj = {"client": "runner", "fun": "jobs.lookup_jid", "jid": jid}
        content = self.post(**obj)
        return content

