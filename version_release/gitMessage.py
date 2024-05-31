import requests
import time

project_result = {}
# 防重处理
all_commits = {}
base_url = 'https://git.fcb.com.cn/api/v4'

# from FasterRunner.settings.pro import DATABASES

# host = '10.101.42.80'
# user='root'
# password='123456'
host = '127.0.0.1'
user='root'
password='root'

def get_data(url):
    headers = {
        "PRIVATE-TOKEN": 'QztPBop5NJdt1vnKRukN'
    }
    rs = []
    try:
        r = requests.get(url, headers=headers)
    except Exception as e:
        print('raise Exception')
    else:
        rs = r.json()
    return rs



def get_projects():  # 根据page，获取所有项目
    url = base_url+"/groups?simple=yes&per_page=20"
    pages = 1
    page_url = url + '&page=' + str(pages)
    rs = get_data(page_url)
    while True:
        if rs == []:
            break
        else:
            for project in rs:
                import pymysql
                connect=pymysql.Connect(
                    host=host,
                    port=3306,
                    user=user,
                    passwd=password,
                    db='version_release',
                    charset='utf8'
                )
                cursor = connect.cursor()
                sql = "INSERT INTO version_release_gitprodata (project_id, project_name,ssh_url_to_repo,http_url_to_repo) VALUES ('%s','%s','%s','%s')"
                data = (str(project['id']), str(project['name']),str(project['ssh_url_to_repo']),str(project['http_url_to_repo']))
                cursor.execute(sql % data)
                connect.commit()
            pages += 1
            page_url = url + '&page=' + str(pages)
            rs = get_data(page_url)
    time.sleep(1)

#得到工程名称的ID
def get_projects_id():  # 根据page，获取所有项目
    url = base_url+"/groups?simple=yes&per_page=20"
    pages = 1
    page_url = url + '&page=' + str(pages)
    rs = get_data(page_url)
    projects_results = []
    while True:
        if rs == []:
            break
        else:

            for project in rs:
                project_id=project['id']
                projects_results.append(project_id)
        pages += 1
        page_url = url + '&page=' + str(pages)
        rs = get_data(page_url)
    return projects_results

# 得到工程名称的ID
def get_projects_programme_id():  # 根据page，获取所有项目
    import pymysql
    connect = pymysql.Connect(
        host=host,
        port=3306,
        user=user,
        passwd=password,
        db='version_release',
        charset='utf8'
    )
    cursor = connect.cursor()
    delete_sql = "TRUNCATE TABLE version_release_gitprogrammedata"
    cursor.execute(delete_sql)
    url = base_url + "/groups/"
    lists = get_projects_id()
    for i in lists:
        page_url = url+ str(i)
        rs = get_data(page_url)

        programe_id = str(rs['id'])
        programe_name = rs['name']
        for pro in rs['projects']:
            project_id=pro['id']
            progranme_name = pro['name']
            ssh_url_to_repo = pro['ssh_url_to_repo']
            http_url_to_repo = pro['http_url_to_repo']
            sql = "INSERT INTO version_release_gitprogrammedata (programme_id,programme_name,project_id, project_name,ssh_url_to_repo,http_url_to_repo) VALUES ('%s','%s','%s','%s','%s','%s')"
            data = (str(programe_id), str(programe_name), str(project_id),str(progranme_name),str(ssh_url_to_repo),str(http_url_to_repo))
            cursor.execute(sql % data)
            connect.commit()

    time.sleep(1)

if __name__ == '__main__':
    get_projects_programme_id()

