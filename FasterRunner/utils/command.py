# -*- coding: utf-8 -*-
import platform
import subprocess
import paramiko
from .logging import logger


class SubCmd(object):
    @staticmethod
    def execute(cmd):
        logger.info('execute cmd: {}'.format(cmd))
        if platform.version() == 'Windows':
            cmd = 'd: && ' + cmd
        sub = subprocess.run(cmd,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out_string = sub.stdout if sub.returncode == 0 else sub.stderr

        try:
            out = out_string.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(e)
            out = out_string.decode('utf-8')
            logger.error('execute result: {}'.format(out))
            raise
        logger.info('execute result: {}'.format(out))
        return out


class ShellClient(SubCmd):
    def __init__(self, host, username='hdbuser', pwd='hdb@1qaz', port=22, ):
        self.host = host
        self.port = port
        self.username = username
        self.pwd = pwd
        self.__k = None
        self._transport = None
        self.connect()

    def connect(self):
        self._transport = paramiko.Transport((self.host, self.port))
        self._transport.connect(username=self.username, password=self.pwd)

    def close(self):
        self._transport.close()

    @staticmethod
    def to_str(bytes_or_str):
        """
        把byte类型转换为str
        :param bytes_or_str:
        :return:
        """
        if isinstance(bytes_or_str, bytes):
            value = bytes_or_str.decode('utf-8')
        else:
            value = bytes_or_str
        return value

    def run_cmd(self, command):
        """
         执行shell命令,返回字典
         return {'color': 'red','res':error}或
         return {'color': 'green', 'res':res}
        :param command:
        :return:
        """
        with paramiko.SSHClient() as _ssh:
            _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 执行命令
            _ssh._transport = self._transport
            stdin, stdout, stderr = _ssh.exec_command(command)
            # 获取命令结果
            res = self.to_str(stdout.read())
            # 获取错误信息
            error = self.to_str(stderr.read())

        # 如果有错误信息，返回error 否则返回res
        out = error if error.strip() else res
        return out

    def upload(self, local_path, target_path):
        # 连接，上传
        with paramiko.SFTPClient.from_transport(self._transport) as sftp:
            sftp.put(local_path, target_path)

    def download(self, target_path, local_path):
        # 连接，下载
        with paramiko.SFTPClient.from_transport(self._transport) as sftp:
            sftp.get(target_path, local_path)


class KubectlJacocoCmd(SubCmd):
    """
    容器化Jacoco命令操作
    操作手册：https://wiki.fcb.com.cn/pages/viewpage.action?pageId=49973901
    """

    def __init__(self, env='sit', host='http://10.71.176.92'):
        self.host = host
        self.env = env

    def kubectl_jacoco_agent_cmd(self, server_name):
        return r"export KUBECONFIG=~/.kube/dev && kubectl get service -n %s-fcb | " \
               r"awk '/8081/ {print $1, $5}' | grep %s | " \
               r"""sed -e 's/8080:.*,8081://g' -e 's/\/TCP//g' | awk ' {print $1 " %s:" $2}'""" % \
               (self.env, server_name, self.host)

    def kubectl_download_jar_cmd(self, server_name, dst_path):
        """
        下载服务jar命令
        :param server_name:
        :param dst_path:
        :return:
        """
        return r"export KUBECONFIG=~/.kube/dev && name=$(kubectl -n {env}-fcb get pods " \
               r"--field-selector=status.phase=Running -l " \
               r"app.kubernetes.io/instance={server_name} --no-headers --output=custom-columns='NAME:.metadata.name' " \
               r"| head -n 1)  && kubectl -n {env}-fcb cp $name:/app.jar {dst_path}" \
            .format(env=self.env, server_name=server_name, dst_path=dst_path)

    def get_jacoco_agent(self, server_name):
        """
        查询到jacocoAgent信息
        :param server_name:
        :return:servername http://ip:port
        """
        cmd = self.kubectl_jacoco_agent_cmd(server_name)
        agent = self.execute(cmd)
        logger.debug('jacocoAgent: %s' % agent)
        jcc_agent_lst = agent.splitlines()
        return jcc_agent_lst

    def download_server_jar(self, server_name, dst_path):
        """
        下载指定服务的当前部署jar包
        :param server_name:
        :param dst_path:
        :return:
        """
        cmd = self.kubectl_download_jar_cmd(server_name, dst_path)
        self.execute(cmd)
