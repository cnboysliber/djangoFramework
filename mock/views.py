import json
from urllib import parse as url_parse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils.encoding import escape_uri_path
from django.db.models import Q
from mock import const as cnt
from mock.utils import logger
from mock.models import ApiMock,ConditionMockRes
from django.http import JsonResponse,HttpResponse
from mock.apiTestApi.commonApiFunction.Utils import parse_request_param
from mock.commonFunction.querysetChangeJson import queryset_change_json, obj_to_dict


@require_http_methods(['POST'])
def add_mock(request):
    """
    新增mock信息
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '新增成功'
    }
    params = {k: v[0] for k, v in dict(request.POST).items() if v and k != 'fileRaw'}
    logger.info(params)
    if request.POST.get('expectValue') == 'application/octet-stream':
        file = request.FILES['fileRaw']
        params['fileName'] = file.name
        params['respData'] = file.read().hex()
    ApiMock.objects.create(**params)
    return JsonResponse(response)


@require_http_methods(['POST'])
def del_mock(request):
    """
    删除mock数据
    :param request:
    :return:
    """
    mock_ids = json.loads(request.POST.get('apiMockId'))
    if not isinstance(mock_ids, list):
        mock_ids = [mock_ids]
    ApiMock.objects.filter(id__in=mock_ids).update(status=cnt.ConstNotActive)
    response = {
        'Code': 100,
        'msg': '删除MOCK成功'
    }
    return JsonResponse(response)


@require_http_methods(['POST'])
def modify_mock(request):
    """
    更新MOCK
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '更新MOCK成功'
    }
    params = {k: v[0] for k, v in dict(request.POST).items() if v and k != 'fileRaw'}
    logger.info(params)
    if request.POST.get('expectValue') == 'application/octet-stream':
        file = request.FILES['fileRaw']
        params['fileName'] = file.name
        params['respData'] = file.read().hex()
    id = params.pop('id')
    ApiMock.objects.filter(id=id, status=cnt.ConstActive).update(**params)
    return JsonResponse(response)


@require_http_methods(['POST'])
def get_mock_info(request):
    """
    插叙单个mock信息
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '查询成功'
    }
    mock_id = request.POST.get('apiMockId')
    mock_info = ApiMock.objects.filter(id=mock_id,
                                       status=cnt.ConstActive)
    response['data'] = queryset_change_json(mock_info)[0]
    return JsonResponse(response)


@require_http_methods(['POST'])
def get_mock_list(request):
    """
    查询mock列表信息
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '查询成功'
    }
    key_word = request.POST.get('keyWord', '')
    page_size = request.POST.get('pageSize')
    page_number = request.POST.get('pageNum')
    mock_list = ApiMock.objects.filter(Q(apiEnv__contains=key_word) |
                                       Q(apiName__contains=key_word) |
                                       Q(expectName__contains=key_word) |
                                       Q(expectValue__contains=key_word) |
                                       Q(respData__contains=key_word))\
        .filter(status=cnt.ConstActive)\
        .order_by('-createTime')
    paginator = Paginator(mock_list, page_size)
    count = paginator.count
    mock_list = paginator.page(page_number)
    response['data'] = queryset_change_json(mock_list)
    response['Count'] = count
    return JsonResponse(response)


@require_http_methods(['POST', 'GET'])
def get_mock_data(request, interface=None):
    """
    mock请求返回值
    :param request:
    :param interface:
    :return:
    """
    rest_url = url_parse.unquote(request.build_absolute_uri())
    uri = url_parse.urlsplit(rest_url).path
    interface = interface or uri
    params = {k: int(v[0]) for k, v in url_parse.parse_qs(url_parse.urlparse(rest_url).query).items()}
    rest_data = json.loads(request.body) if 'application/json' in request.content_type else request.POST
    mock_info = ApiMock.objects.filter(apiName=interface, status=cnt.ConstActive).first()
    if not mock_info:
        return HttpResponse(status=404)
    resp_status_code = mock_info.respStatusCode or 200
    resp_headers = mock_info.respHeaders or '{}'
    cnd_obj_list = ConditionMockRes.objects.filter(mockId=mock_info.id, status=cnt.ConstActive)
    if not cnd_obj_list.first() and not params and mock_info.expectValue != 'application/octet-stream':
        response = mock_info.respData

    else:
        def dict2obj(d):
            if isinstance(d, list):
                d = [dict2obj(x) for x in d]
            if not isinstance(d, dict):
                return d

            class C(object):
                pass
            o = C()
            for k in d:
                o.__dict__[k] = dict2obj(d[k])
            return o
        if isinstance(rest_data, dict):
            rest_data = dict(rest_data)
            rest_data.update(params)
        else:
            rest_data = params
        root = dict2obj(rest_data)
        response = mock_info.respData
        for cnd_data in cnd_obj_list:
            resp_status_code = cnd_data.respStatusCode or 200
            condition = cnd_data.condition.replace('&&', ' and ').replace('||', ' or ')
            try:
                result = eval(condition, root.__dict__)
            except Exception as e:
                print(e)
                result = False
            if result is True:
                response = cnd_data.respData
                break
    if mock_info.expectValue == 'application/octet-stream':
        response = HttpResponse(bytes.fromhex(mock_info.respData))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={file_name}' \
            .format(file_name=escape_uri_path(mock_info.fileName))
    else:
        response = parse_request_param([{'resultData': rest_data}], response, False)
        content_type = mock_info.expectValue if mock_info.expectValue == 'text/xml' else 'application/json'
        headers = json.loads(resp_headers)
        response = HttpResponse(response, content_type=content_type, status=resp_status_code)

        for k, v in headers.items():
            response[k] = v
    return response


@require_http_methods(['POST'])
def add_mock_condition(request):
    """
    添加mock条件值
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '添加成功'
    }
    mock_id = request.POST.get('mockId')
    condition = request.POST.get('condition')
    resp_data = request.POST.get('respData')
    resp_status_code = request.POST.get('respStatusCode', 200)
    ConditionMockRes.objects.create(mockId=mock_id, condition=condition,
                                    respData=resp_data, respStatusCode=resp_status_code)
    return JsonResponse(response)

@require_http_methods(['POST'])
def del_mock_condition(request):
    """
    添加mock条件值
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '删除成功'
    }
    condition_id = request.POST.get('conditionId')
    ConditionMockRes.objects.filter(id=condition_id).update(status=cnt.ConstNotActive)
    return JsonResponse(response)

@require_http_methods(['POST'])
def modify_mock_condition(request):
    """
    修改mock条件值
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '更新成功'
    }
    condition_id = request.POST.get('conditionId')
    mock_id = request.POST.get('mockId')
    condition = request.POST.get('condition')
    resp_data = request.POST.get('respData')
    resp_status_code = request.POST.get('respStatusCode', 200)
    ConditionMockRes.objects\
        .filter(id=condition_id)\
        .update(mockId=mock_id, condition=condition,
                respData=resp_data, respStatusCode=resp_status_code)
    return JsonResponse(response)

@require_http_methods(['POST'])
def get_mock_condition_list(request):
    """
    查询mock的所有条件值
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '查询成功'
    }
    mock_id = request.POST.get('mockId')
    condition = request.POST.get('condition', '')
    filters = dict(mockId=mock_id,
                   condition__contains=condition,
                   status=cnt.ConstActive)
    page_num = request.POST.get('pageNum', 1)
    page_size = request.POST.get('pageSize', 10)
    query = ConditionMockRes.objects.filter(**filters)
    paginator = Paginator(query, page_size)
    total_count = query.count()
    query_list = paginator.page(page_num)
    response['Count'] = total_count
    response['data'] = queryset_change_json(query_list)

    return JsonResponse(response)


@require_http_methods(['POST'])
def get_mock_condition_check(request):
    """
    查询mock条件的详情
    :param request:
    :return:
    """
    response = {
        'Code': 100,
        'msg': '查询成功'
    }
    condition_id = request.POST.get('conditionId')
    filters = dict(id=condition_id,
                   status=cnt.ConstActive)
    query = ConditionMockRes.objects.filter(**filters).first()
    response['data'] = obj_to_dict(query)
    return JsonResponse(response)