from urllib.parse import urlparse
import re


def parse_host(ip, api):
    '''
    解析host
    '''
    if not isinstance(ip, list):
        return api
    if not api:
        return api

    #'https://i.cnblogs.com/EditPosts.aspx?opt=1'  通过解析返回：ParseResult(scheme='https', netloc='i.cnblogs.com', path='/EditPosts.aspx', params='', query='opt=1', fragment='')
    try:
        parts = urlparse(api["request"]["interface_path"])   #解析url的参数
    except KeyError:
        parts = urlparse(api["request"]["base_url"])
    # 返回值是Host:port
    host = parts.netloc   #获取域名
    host = host.split(':')[0]  #获取域名端口前的ip
    if host:
        for content in ip:
            content = content.strip()
            if host in content and not content.startswith("#"):
                ip = re.findall(r'\b(?:25[0-5]\.|2[0-4]\d\.|[01]?\d\d?\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b', content)
                # ip = re.findall(r'\b(?:25[0-5]\.|2[0-4]\d\.|[01]?\d\d?\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b:\d{0,5}', content)
                if ip:
                    if "header" in api["request"].keys():
                        api["request"]["header"]["Host"] = host
                    else:
                        api["request"].setdefault("header", {"Host": host})
                    try:
                        api["request"]["interface_path"] = api["request"]["interface_path"].replace(host, ip[-1])
                    except KeyError:
                        api["request"]["base_url"] = api["request"]["base_url"].replace(host, ip[-1])

    return api  #返回处理后的testcase或者config
