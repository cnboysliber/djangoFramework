from copy import deepcopy

from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework.viewsets import GenericViewSet
from interface_runner import models, serializers
from rest_framework.response import Response
from interface_runner.utils import response
from FasterRunner.utils.decorator import request_log
from interface_runner.utils.parser import ErrorProcessor



class GetLogView(GenericViewSet):
    pass