# -*- coding:utf-8 -*-
import os
import json
import time
import shutil
import zipfile
import traceback
import requests
from urllib.parse import urljoin, urlparse, parse_qs

from django.conf import settings

from FasterRunner.utils import logger
from FasterRunner.utils.decorator import handle_db_connections
from FasterRunner.utils.command import ShellClient, KubectlJacocoCmd
from FasterRunner.threadpool import execute
from performApp.models import JacocoService, JacocoTask
from performApp.utils.jenkinsCmd import JenkinsApi

git_token = '6rVB4sNutmx1WS8MmPTL'
# sonar_login = '0bec27fe8e510f2b9fc8f104f5383074364492ab'
sonar_login = '0e53f2d676df70a65e277eb026ebea86a181dffb'
jenkins_user = '042834150'
jenkins_token = '11a4236b0ecbe16ee25bced07819612444'

DOCKER = 0
TOMCAT = 1

NACOS_ENVS = {
    'sit': 'https://nacos-sit.fcb.com.cn',
    'sit2': 'https://nacos-sit2.fcb.com.cn'
}
server_options = {
    'hdb-broker-recommend': 'hdb_recommend',
    'hdb-broker-personal': 'hdb_personal'
}
JENKINS_ENV = {
    '中台服务': 'https://jenkins.fcb.com.cn/job/middleend/job/middleend-sit/'
}


class JacocoTest(object):

    def __init__(self, env, namespace='DEFAULT_GROUP'):
        self.host = NACOS_ENVS.get(env)
        self.namespace = namespace
        self.kubectl = KubectlJacocoCmd(env)

    def nacos_service(self, server_name, clusters='DEFAULT'):
        url = urljoin(self.host, 'nacos/v1/ns/instance/list?serviceName={}&&clusters={}&namespace={}'
                      .format(server_name, clusters, self.namespace))
        logger.info('url: ' + url)
        rest = requests.get(url)
        service = rest.json()
        logger.info('nacos service detail:{}'.format(service))
        if not service:
            raise Exception('nacos服务获取异常')
        return service

    def download_jar(self, server_name, dst_path):
        """
        下载jar包到指定路径
        :param server_name:
        :param dst_path:
        :return:
        """
        self.kubectl.download_server_jar(server_name, dst_path)

    def get_jacoco_agent(self, server_name):
        """
        获取jacocoAgent服务信息
        :param server_name:
        :return: http://ip:port
        """
        return self.kubectl.get_jacoco_agent(server_name)

    @staticmethod
    def copy_properties(src_dir, dest_dir):
        shutil.copy(os.path.join(src_dir, 'sonar-project.properties'), dest_dir)

    @staticmethod
    def get_sonar_cmd(project_key, version, report_paths, project_dir, project_name='',
                      sonar_token=sonar_login, deploy_type='docker'):
        """
        上传报告到sonarQube命令
        :param sonar_token:
        :param project_key:
        :param version:
        :param report_paths:
        :param project_dir:
        :param project_name:
        :param deploy_type:
        :return:
        """
        cmd = 'cd {projectDir} && sonar-scanner -Dsonar.login={sonarlogin} ' \
              '-Dsonar.projectName={projectName} ' \
              '-Dsonar.projectKey={sonarprojectKey} ' \
              '-Dsonar.projectVersion={sonarprojectVersion} ' \
              '-Dsonar.jacoco.reportPaths={reportPaths}'.format(sonarlogin=sonar_token,
                                                                sonarprojectKey=project_key,
                                                                sonarprojectVersion=version,
                                                                reportPaths=report_paths,
                                                                projectDir=project_dir,
                                                                projectName=project_name)
        if deploy_type == TOMCAT:
            cmd += ' -Dsonar.java.binaries=target/WEB-INF/classes -Dsonar.java.libraries=target/WEB-INF/lib' \
                   f' -Dsonar.sources={project_dir}'
        return cmd

    @staticmethod
    def clone_project(url, dest_path, tag, commit_id=None):
        if os.path.exists(dest_path):
            cmd = 'cd {} && git fetch && git checkout {} && git checkout -f {}' \
                .format(dest_path, tag, commit_id)
        else:
            cmd = 'git clone {url} {dest_path} && cd {dest_path} ' \
                  '&& git checkout {tag} && git checkout -f {commitID}' \
                .format(url=url, dest_path=dest_path, tag=tag, commitID=commit_id)
        return ShellClient.execute(cmd)

    @staticmethod
    def merge_exec_report(service_name, exec_dir, jacococli_dir='Tool', sufix='*'):
        src_exec_path = os.path.join(exec_dir, '*_{sufix}.exec'.format(sufix=sufix))
        dest_exec_path = os.path.join(exec_dir, f'{service_name}-{sufix}.exec')
        cmd = 'cd {jacococli_dir} && java -jar jacococli.jar merge {src_exec_path} --destfile {dest_exec_path}' \
            .format(service_name=service_name,
                    jacococli_dir=jacococli_dir,
                    src_exec_path=src_exec_path,
                    dest_exec_path=dest_exec_path)
        return ShellClient.execute(cmd)

    @staticmethod
    def dump_jacoco_report(host, port, exec_path, jacoco_path):
        cmd = 'cd {jacoco_path} && java -jar jacococli.jar dump --address {host} ' \
              '--port {port} --destfile {exec_path}' \
            .format(jacoco_path=jacoco_path, host=host, port=port, exec_path=exec_path)
        logger.info('jacoco dump cmd: {}'.format(cmd))
        out = ShellClient.execute(cmd)
        return out

    @staticmethod
    def unzip_jar(zip_path, dest_path='projectCode'):
        """
        解压jar文件到指定目录
        :param zip_path: jar的绝对路劲
        :param dest_path: 默认解压到当前路劲下的target目录
        :return:
        """
        dest_path = os.path.join(dest_path, 'target')
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        else:
            shutil.rmtree(dest_path)

        zip_file = zipfile.ZipFile(zip_path)
        for zip_name in zip_file.namelist():
            zip_file.extract(zip_name, dest_path)


def get_git_path_by_name(service_name):
    """
    获取服务git路径
    :param service_name:
    :return:
    """
    url = 'https://git.fcb.com.cn/api/v4/projects?search={service_name}'
    headers = {
        "Authorization": "Bearer {}".format(git_token)
    }
    resp = requests.get(url.format(service_name=service_name), headers=headers)
    srv_list = resp.json()
    logger.debug(srv_list)
    if not (resp.status_code == 200 and srv_list):
        logger.error("git路径获取失败，请检查是否有权限访问改服务仓库")
        raise Exception("git路径获取失败，请检查是否有权限访问改服务仓库")
    for srv in srv_list:
        if srv['name'] == service_name:
            return srv.get('http_url_to_repo')
    else:
        raise Exception("git路径获取失败，请检查是否有权限访问改服务仓库")


def get_jenkins_job_build_info(service_name, module, jenkins_job=None):
    """
    查询服务编译信息
    :param service_name:
    :param module:
    :param jenkins_job:
    :return:
    """
    url = JENKINS_ENV[module]
    jk = JenkinsApi(url, jenkins_user, jenkins_token)
    if jenkins_job:
        job = jk.get_job_info(jenkins_job)
    else:
        jobs = jk.get_job_info_regex(service_name)
        if len(jobs) > 1 or len(jobs) == 0:
            raise Exception('jenkins上存在多个job或不存在该服务')

        job = jobs[0]
    display_name = job['displayName']
    build_info = jk.get_last_success_build_info(display_name)
    sonar_class = 'hudson.plugins.sonar.action.SonarAnalysisAction'
    git_class = 'hudson.plugins.git.util.BuildData'
    git_remote = ''
    git_commit_id = ''
    git_branch = ''
    sonar_key = ''
    try:
        for action in build_info['actions']:
            if not action.get('_class'):
                continue
            if action['_class'] == git_class:
                git_remote = action['remoteUrls'][0]
                git_commit_id = action['lastBuiltRevision']['SHA1']
                git_branch = action['lastBuiltRevision']['branch'][0]['name']
            elif action['_class'] == sonar_class:
                sonarqube_dashboard_url = action['sonarqubeDashboardUrl']
                ps = urlparse(sonarqube_dashboard_url)
                sonar_key = parse_qs(ps.query).get('id')[0]
    except Exception as e:
        logger.error(str(e))
        raise Exception('获取jenkins编译信息失败：%s' % str(e))
    return git_remote, git_commit_id, git_branch, sonar_key


@handle_db_connections
def run_jacoco(service_id, env='sit', **kwargs):
    """

    :param service_id:
    :param env:
    :param kwargs:
    :return:
    """
    running = 1
    success = 2
    fail = 3
    state = success
    logger.info('覆盖率收集任务开始运行...')
    logs = ['覆盖率收集任务开始运行:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S'))]
    task_uid = ''
    try:
        run_stamp = int(time.time())
        obj = JacocoTask.objects.create(service_id=service_id, state=running)
        task_uid = obj.uid
        service_obj = JacocoService.objects.get(id=service_id)
        service_name = service_obj.service_name
        nacos_name = service_obj.nacos_name or service_name
        module = service_obj.module
        jenkins_job = service_obj.jenkins_job
        deploy_type = service_obj.dtype
        # jacoco_port_type = service_obj.jacoco_port_type
        sonar_project_key = service_obj.sonar_project_key

        git_remote = service_obj.git_path
        if not service_obj.git_path:
            git_remote = get_git_path_by_name(service_name)

        logger.info('git_remote: {}'.format(git_remote))
        git_server_name = os.path.split(git_remote)[-1][:-len('.git')] if git_remote else ''

        base_dir, cover_dir = settings.BASE_DIR, settings.COVER_DIR

        coverage_dir = os.path.abspath(os.path.join(cover_dir, 'exec',
                                                    service_name))
        jar_dir = os.path.abspath(os.path.join(cover_dir, 'jar',
                                               service_name))
        project_path = os.path.abspath(os.path.join(cover_dir, 'projectCode', service_name))
        service_exec_path = os.path.join(coverage_dir, f'{service_name}-{str(run_stamp)}.exec')
        tool_dir = os.path.abspath(os.path.join(cover_dir, 'Jacoco'))
        jar_path = os.path.join(jar_dir, f'{service_name}.jar')
        sonar_properties_dir = os.path.join(base_dir, 'templates')
        for path in [coverage_dir, jar_dir, tool_dir]:
            if not os.path.exists(path):
                os.makedirs(path)

        jacoco = JacocoTest(env)
        if deploy_type == DOCKER:
            logs.append('查询服务在nacos上详情信息')
            nacos_service = jacoco.nacos_service(nacos_name)
            if not nacos_service:
                logs.append('nacos未发现服务')
                raise
            commit_id = nacos_service['hosts'][0]['metadata'].get('git.commit.id', '')
            sonarproject_key = sonar_project_key or 'com.evergrande.cloud:{}'.format(service_name)
            version = nacos_service['hosts'][0]['metadata'].get('git.build.version', '')
            if nacos_service['hosts'][0]['metadata'].get('git.branch', ''):
                branch = nacos_service['hosts'][0]['metadata'].get('git.branch', '')
            elif nacos_service['hosts'][0]['metadata'].get('git.tags'):
                branch = nacos_service['hosts'][0]['metadata'].get('git.tags').split(',')[0]
            else:
                branch = 'origin/test'

            logs.append('收集Jacoco部署服务器信息')

            jcc_agent_lst = jacoco.get_jacoco_agent(git_server_name)
            if not jcc_agent_lst:
                raise Exception('jacocoAgent未部署在服务器上')
            logs.append('Jacoco部署服务器：{}'.format(','.join(jcc_agent_lst)))
        else:
            logs.append('查询服务jenkins构建信息')
            jcc_agent_lst = service_obj.server_ip.split(',')
            git_remote, commit_id, branch, sonarproject_key = get_jenkins_job_build_info(module=module,
                                                                                         service_name=service_name,
                                                                                         jenkins_job=jenkins_job)
            version = branch
            if sonarproject_key:
                JacocoService.objects.filter(id=service_id).update(sonar_project_key=sonarproject_key)
        if deploy_type == TOMCAT:
            clone_path = git_remote.replace('//', '//jacoco:RUa9sGzkjuVZgwXFnx99@')
        elif service_obj.git_path:
            clone_path = git_remote.replace('//', '//jacoco:RUa9sGzkjuVZgwXFnx99@')
        else:
            clone_path = get_git_path_by_name(service_name).replace('//', '//jacoco:RUa9sGzkjuVZgwXFnx99@')

        logs.append('下载服务对应的部署jar/war包')

        try:
            # 个别服务在服务器上的目录名有差异
            # server_name = server_options.get(service_name) or service_name
            if deploy_type == DOCKER:
                jacoco.download_jar(git_server_name, jar_path)
            elif deploy_type == TOMCAT:
                ssh = ShellClient(jcc_agent_lst[0])
                ssh.download(service_obj.service_path, jar_path)
            logs.append('下载jar/war成功')
        except Exception as e:
            logger.error(e)
            logs.append('下载jar/war失败')
            raise

        logs.append('收集服务器代码覆盖率报告，并生成exec文件中......')
        try:
            exec_list = []
            dump_results = []
            logger.info('jacoco部署的服务器：{}'.format(jcc_agent_lst))
            coverage_count = 0
            for info in jcc_agent_lst:
                if deploy_type == DOCKER:
                    srv_name, srv_url = info.strip().split()
                    logger.info('git_server_name: {}, srv_name: {}'.format(git_server_name, srv_name))
                    if not srv_name == git_server_name:
                        continue
                    url_parse = urlparse(srv_url)
                    host, port = url_parse.netloc.split(':')
                else:
                    host, port = info, '2{}'.format(service_obj.service_port)
                coverage_count += 1
                exec_path = os.path.join(coverage_dir,
                                         f'{service_name}_{host}_{run_stamp}.exec')
                exec_list.append(f'{service_name}_{host}_{run_stamp}.exec')
                report = jacoco.dump_jacoco_report(host, port, exec_path, tool_dir)
                dump_results.append(report)
            if coverage_count == 0:
                raise Exception('未检测到jacocoAgent服务，请确认JACOCO部署是否成功')
            logs.append('收集服务器代码覆盖率报告完成：{}'.format(','.join(dump_results)))
        except Exception as e:
            logger.error(traceback.format_exc())
            logs.append('收集服务器代码覆盖率异常：{}'.format(e))
            raise

        logs.append('正在合并生成exec文件......')
        if os.path.exists(service_exec_path):
            os.remove(service_exec_path)
        merge_out = jacoco.merge_exec_report(service_name, coverage_dir, jacococli_dir=tool_dir, sufix=str(run_stamp))
        logs.append('合并完成:\n{}'.format(merge_out))

        # clone源代码到本地，报告分析需要使用源代码
        logs.append('正在通过git服务器克隆源代码......')
        jacoco.clone_project(clone_path, project_path, branch, commit_id)
        logs.append('源代码克隆成功')
        # 解压jar包，用于代码报告上传需要字节码
        logger.info('jar_path:' + jar_dir)
        logger.info('project_path:' + project_path)

        logs.append(f'解压服务jar/war文件包, 目录：\n{jar_dir}')

        jacoco.unzip_jar(jar_path, project_path)
        logs.append('解压服务jar/war文件包成功')
        jacoco.copy_properties(sonar_properties_dir, project_path)
        sonar_cmd = jacoco.get_sonar_cmd(sonarproject_key,
                                         version,
                                         service_exec_path,
                                         project_path,
                                         service_name, deploy_type=deploy_type)
        logs.append('报告生成命令：{}'.format(sonar_cmd))
        logs.append('报告正在上传sonarqube, 请耐心等待....')
        JacocoTask.objects.filter(uid=task_uid).update(state=state, log=json.dumps(logs))
        result = ShellClient.execute(sonar_cmd)

        if 'EXECUTION FAILURE' in result:
            logger.error('上传覆盖率失败：' + service_name + ' \n错误：' + result)
            state = fail
        else:
            logs.append('报告上传成功\n%s' % result)
    except Exception as e:
        print(traceback.format_exc())
        logger.error(str(traceback.format_exc()))
        logs.append(str(e))
        state = fail
    finally:
        JacocoTask.objects.filter(uid=task_uid).update(state=state, log=json.dumps(logs))
    return state, logs


def async_run_jacoco(service_id, env='sit', **kwargs):
    """

    :param service_id:
    :param env:
    :param kwargs:
    :return:
    """
    ret = execute.submit(run_jacoco, service_id, env=env, **kwargs)
    return ret


def batch_execute(service_id_lst, env='sit', **kwargs):
    """
    批量运行代码覆盖率
    :param service_id_lst:
    :param env:
    :param kwargs:
    :return:
    """
    results = []
    for service_id in service_id_lst:
        ret = async_run_jacoco(service_id, env=env, **kwargs)
        results.append(ret)
    # as_completed(results)
