from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from FasterRunner import pagination
from interface_runner import models, serializers
from FasterRunner.utils.decorator import request_log
from interface_runner.pytest_run.run import RunCase


class RunCaseView(ListModelMixin,GenericViewSet):
    queryset = models.Project.objects.all().order_by('-update_time')
    serializer_class = serializers.ProjectSerializer
    pagination_class = pagination.MyCursorPagination

    @method_decorator(request_log(level="INFO"))
    def add(self,request):
        #serializer = SnippetSerializer(data=request.data)
        data=request.data
        body=data["body"]
        RunCase().run_main(body)
        return Response({"code":"0001","msg":"用例正在运行"})
