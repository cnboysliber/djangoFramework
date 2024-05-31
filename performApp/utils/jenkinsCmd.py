from jenkins import Jenkins


class JenkinsApi(object):
    def __init__(self, url, username=None, password=None):
        self.client = Jenkins(url, username, password)

    def get_job_info(self, name, depth=0, fetch_all_builds=False):
        """
        查询job信息
        :param name:
        :param depth:
        :param fetch_all_builds:
        :return:
        """
        return self.client.get_job_info(name, depth, fetch_all_builds)

    def get_jobs(self, folder_depth=0):
        """
        查询获取jobs
        :param folder_depth:
        :return:
        """
        return self.client.get_jobs(folder_depth=folder_depth)

    def get_job_info_regex(self, name):
        """
        查询jobs信息
        """
        job_lst = self.client.get_job_info_regex(name)
        return job_lst

    def get_last_success_build_info(self, name):
        """
        获取最后一次编译成功的信息
        :param name:
        :return:
        """
        info = self.get_job_info(name)
        number = info['lastSuccessfulBuild']['number']
        return self.client.get_build_info(name, number)

    def get_nodes(self, depth=0):
        return self.client.get_nodes(depth=depth)

    def get_job_config(self, name):
        """
        查询配置
        """
        return self.client.get_job_config(name)



