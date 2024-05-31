from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from interface_runner.models import Visit
import logging

logger = logging.getLogger()


class VisitTimesMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 复制一份body的内容，因为原生的body不能被多次访问
        request._body = request.body

    def process_response(self, request, response):

        body = request._body
        if body == b'':
            body = ""
        elif isinstance(body, bytes):
            body = 'upload file'
        else:
            body = str(body, encoding='utf-8')

        if request.user is None:
            # 报告页面不需要登录，获取不到用户名
            user = 'AnonymousUser'
        else:
            user = request.user

        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        # 前端请求头没传project，就默认为0
        project = request.META.get('Project', 0)

        url: str = request.path
        # 去除测试报告页字体相关的访问
        if '/fonts/roboto/' in url:
            return response

        if request.GET != {}:
            query_params = '?'
            # <QueryDict: {'page': ['1'], 'node': [''], 'project': ['11'], 'search': [''], 'tag': ['']}>
            for k, v in request.GET.items():
                query_params += f'{k}={v}&'
            url += query_params[:-1]
        else:
            query_params = ''

        Visit.objects.create(user=user, url=url, request_method=request.method, request_body=body, ip=ip,
                             path=request.path, request_params=query_params[1:-1], project=project)
        return response
