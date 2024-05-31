from loguru import logger
import json
import datetime
import threading
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from interface_runner.utils import loader, response
from interface_runner import tasks
from rest_framework.response import Response
from FasterRunner.utils.decorator import request_log
from interface_runner.utils.host import parse_host
from interface_runner.utils.parser import Format
from interface_runner.utils.prepare import get_db_processor
from interface_runner import models
from dwebsocket.decorators import accept_websocket, require_websocket

"""运行方式
"""

config_err = {
    "success": False,
    "msg": "指定的配置文件不存在",
    "code": "9999"
}


@api_view(['POST'])
@request_log(level='INFO')
def run_api(request):
    """ run api by body
    """
    name = request.data.pop('config')
    host = request.data.pop("host")
    api = Format(request.data)
    api.parse()

    config = None
    if name != '请选择':
        try:
            config = eval(models.Config.objects.get(name=name, project__id=api.project).body)

        except ObjectDoesNotExist:
            logger.error("指定配置文件不存在:{name}".format(name=name))
            return Response(config_err)

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project__id=api.project).value.splitlines()
        api.testcase = parse_host(host, api.testcase)

    report_name = loader.debug_api(api.testcase, api.project, name=api.name, config=parse_host(host, config),
                                   user=request.user)

    try:

        summary = models.Report.objects.get(name=report_name)
        response.REPORT_GET_SUCCESS['results'] = {
            "name": summary.name,
            "id": summary.id,
            "summary": eval(summary.summary),
        }
        return Response(response.REPORT_GET_SUCCESS)

    except Exception as e:

        return Response(response.REPORT_GET_FAILE)


@api_view(['GET'])
@request_log(level='INFO')
def run_api_pk(request, **kwargs):
    """run api by pk and config
    """
    ac_config = request.query_params["ac_config"]
    api = models.API.objects.get(id=kwargs['pk'])
    config = request.query_params["config"]
    env_id = request.query_params["env_id"]
    project = request.query_params['project']
    host = "请选择"

    # config = None if name == '请选择' else eval(models.Config.objects.get(name=name, project=api.project).body)

    test_case = eval(api.body)
    if env_id:
        env_name = models.Env.objects.get(id=env_id).name

    if project:
        project_name = models.Project.objects.get(id=project).name
        db_obj = list(models.DBConfig.objects.filter(project_id=project, env_id=env_id).values('db_name', 'db_info'))
        db_data = get_db_processor(db_obj)

    if ac_config != "请选择":
        ac_config = models.AccountConfig.objects.filter(project=project, ac_name=ac_config).values('ac_name',
                                                                                                   'ac_info',
                                                                                                   'fixture_id').first()
        fixture_code = models.Fixture.objects.get(project=project, id=ac_config['fixture_id']).code
        ac_config['fixture_code'] = fixture_code

    if config != "请选择":
        # 返回config表里面的每个字段的值（键值对）
        config = eval(models.Config.objects.get(project=project,
                                                name=config).body)

    report_name = loader.debug_api(test_case,
                                   project,
                                   ac_config=ac_config,
                                   name=api.interface_name,
                                   report_name="",
                                   env_name=env_name,
                                   project_name=project_name,
                                   db_data=db_data,
                                   config=parse_host(host, config),
                                   user=request.user.username)
    try:

        summary = models.Report.objects.get(name=report_name)
        response.REPORT_GET_SUCCESS['results'] = {
            "name": summary.name,
            "id": summary.id,
            "summary": eval(summary.summary),
        }
        return Response(response.REPORT_GET_SUCCESS)

    except Exception as e:

        return Response(response.REPORT_GET_FAILE)


def auto_run_api_pk(**kwargs):
    """run api by pk and config
    """
    id = kwargs['id']
    env = kwargs['config']
    config_name = 'rig_prod' if env == 1 else 'rig_test'
    api = models.API.objects.get(id=id)
    config = eval(models.Config.objects.get(name=config_name, project=api.project).body)
    test_case = eval(api.body)

    summary = loader.debug_api(test_case, api.project.id, config=config)
    api_request = summary['details'][0]['records'][0]['meta_data']['request']
    api_response = summary['details'][0]['records'][0]['meta_data']['response']

    # API执行成功,设置tag为自动运行成功
    if summary['stat']['failures'] == 0 and summary['stat']['errors'] == 0:
        models.API.objects.filter(id=id).update(tag=3)
        return 'success'
    elif summary['stat']['failures'] == 1:
        # models.API.objects.filter(id=id).update(tag=2)
        return 'fail'


def update_auto_case_step(**kwargs):
    """
    {'name': '查询关联的商品推荐列表-小程序需签名-200014-生产',
    'body': {'name': '查询关联的商品推荐列表-小程序需签名-200014-生产',
    'rig_id': 200014, 'times': 1,
    'request': {'url': '/wxmp/mall/goods/detail/getRecommendGoodsList',
    'method': 'GET', 'verify': False, 'headers': {'wb-token': '$wb_token'},
    'params': {'goodsCode': '42470'}}, 'desc': {'header': {'wb-token': '用户登陆token'}, 'data': {}, 'files': {},
    'params': {'goodsCode': '商品编码'}, 'variables': {'auth_type': '认证类型', 'rpc_Group': 'RPC服务组',
    'rpc_Interface': '后端服务接口', 'params_type': '入参数形式', 'author': '作者'}, 'extract': {}},
    'validate': [{'equals': ['content.info.error', 0]}], 'variables': [{'auth_type': 5},
    {'rpc_Group': 'wbiao.seller.prod'}, {'rpc_Interface': 'cn.wbiao.seller.api.GoodsDetailService'},
    {'params_type': 'Key_Value'}, {'author': 'xuqirong'}], 'setup_hooks': ['${get_sign($request,$auth_type)}']},
    'url': '/wxmp/mall/goods/detail/getRecommendGoodsList', 'method': 'GET', 'step': 5}
    :param kwargs:
    :return:
    """
    # 去掉多余字段
    kwargs.pop('project')
    kwargs.pop('rig_id')
    kwargs.pop('relation')

    # 测试环境0,对应97 生产环境1,对应98
    rig_env = kwargs.pop('rig_env')
    case_id = 98 if rig_env == 1 else 97
    # 获取case的长度,+1是因为增加了一个case_step,
    length = models.Case.objects.filter(id=case_id).first().length + 1
    # case的长度也就是case_step的数量
    kwargs['step'] = length
    kwargs['case_id'] = case_id
    case_step_name = kwargs['name']
    # api不存在用例中,就新增,已经存在就更新
    is_case_step_name = models.CaseSuitInfo.objects.filter(case_id=case_id).filter(name=case_step_name)
    if len(is_case_step_name) == 0:
        models.CaseSuit.objects.filter(id=case_id).update(length=length, update_time=datetime.datetime.now())
        models.CaseSuitInfo.objects.create(**kwargs)
    else:
        is_case_step_name.update(update_time=datetime.datetime.now(), **kwargs)


@api_view(['POST'])
@request_log(level='INFO')
def run_api_tree(request):
    """run api by tree
    {
        project: int
        relation: list
        name: str
        async: bool
        host: str
    }
    """
    # order by id default
    host = request.data["host"]
    project = request.data['project']
    relation = request.data["relation"]
    back_async = request.data["async"]
    report_name = request.data["name"]
    config = request.data["config"]
    ac_config = request.data["ac_config"]
    env_id = request.data["env_id"]

    test_case = []

    if config != '请选择':
        config = eval(models.Config.objects.get(name=config, project__id=project).body)

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project=project).value.splitlines()

    for relation_id in relation:
        api = models.API.objects.filter(project__id=project, relation=relation_id, delete=0).order_by('id').values(
            'body')  # 获取所有选中节点api
        for content in api:
            api = eval(content['body'])
            test_case.append(parse_host(host, api))

    if env_id:
        env_name = models.Env.objects.get(id=env_id).name

    if project:
        project_name = models.Project.objects.get(id=project).name
        db_obj = list(models.DBConfig.objects.filter(project_id=project, env_id=env_id).values('db_name', 'db_info'))
        db_data = get_db_processor(db_obj)

    if ac_config != "请选择":
        ac_config = models.AccountConfig.objects.filter(project=project, ac_name=ac_config).values('ac_name',
                                                                                                   'ac_info',
                                                                                                   'fixture_id').first()
        fixture_code = models.Fixture.objects.get(project=project, id=ac_config['fixture_id']).code
        ac_config['fixture_code'] = fixture_code

    if back_async:
        tasks.async_debug_api.delay(test_case,
                                    project,
                                    ac_config=ac_config,
                                    name=None,
                                    report_name=report_name,
                                    env_name=env_name,
                                    project_name=project_name,
                                    db_data=db_data,
                                    config=parse_host(host, config),
                                    save=True,
                                    run_type=2,
                                    user=request.user)

        summary = loader.TEST_NOT_EXISTS
        summary["msg"] = "接口运行中，请稍后查看报告"
    else:
        report_name = loader.debug_api(test_case,
                                   project,
                                   ac_config=ac_config,
                                   name=f'批量运行{len(test_case)}条API',
                                   report_name="",
                                   env_name=env_name,
                                   project_name=project_name,
                                   db_data=db_data,
                                   config=parse_host(host, config),
                                   save=True,
                                   user=request.user)

        try:

            summary = models.Report.objects.get(name=report_name)
            response.REPORT_GET_SUCCESS['results'] = {
                "name": summary.name,
                "id": summary.id,
                "summary": eval(summary.summary),
            }
            return Response(response.REPORT_GET_SUCCESS)

        except Exception as e:

            return Response(response.REPORT_GET_FAILE)


@api_view(["POST"])
@request_log(level='INFO')
def run_testsuite(request):
    """debug testsuite
    {
        name: str,
        body: dict
        host: str
    }
    """
    body = request.data["body"]
    project = request.data["project"]
    name = request.data["name"]
    host = request.data["host"]

    test_case = []
    config = None

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project=project).value.splitlines()

    for test in body:
        test = loader.load_test(test, project=project)
        if "base_url" in test["request"].keys():
            config = test
            continue

        test_case.append(parse_host(host, test))

    report_name= loader.debug_api(test_case, project, name=name, config=parse_host(host, config), user=request.user)

    try:

        summary = models.Report.objects.get(name=report_name)
        response.REPORT_GET_SUCCESS['results'] = {
            "name": summary.name,
            "id": summary.id,
            "summary": eval(summary.summary),
        }
        return Response(response.REPORT_GET_SUCCESS)

    except Exception as e:


        return Response(response.REPORT_GET_FAILE)


# @api_view(["POST"])
# @accept_websocket
# @request_log(level='INFO')
# def run_testsuite_websocket(request):
#     """debug testsuite
#     {
#         name: str,
#         body: dict
#         host: str
#     }
#     """
#     body = request.data["body"]
#     project = request.data["project"]
#     name = request.data["name"]
#     host = request.data["host"]
#
#     test_case = []
#     config = None
#
#     if project:
#         project_name=models.Project.objects.get(id=project).name
#
#     if host != "请选择":
#         host = models.HostIP.objects.get(name=host, project=project).value.splitlines()
#
#     for test in body:
#         test = loader.load_test(test, project=project)
#         if "base_url" in test["request"].keys():
#             config = test
#             continue
#
#         test_case.append(parse_host(host, test))
#
#     summary = loader.debug_api_websocket(test_case, project,project_name,name=name, config=parse_host(host, config), user=request.user)
#     for output in summary:
#         request.websocket.send(output)
#
#     #return Response(summary)

# def change_type(obj):
#     if isinstance(obj,bytes):
#         return str(obj,encoding='utf-8')
#     return json.JSONEncoder.default(obj)


@api_view(["GET"])
@request_log(level='INFO')
def run_testsuite_pk(request, **kwargs):
    """run testsuite by pk
        {
            project: int,
            name: str,
            host: str
        }
    """
    pk = kwargs["pk"]  # pk为case_id
    project = request.query_params["project"]
    suit_name = request.query_params["suit_name"]
    host = request.query_params["host"]  # 获取host_name
    back_async = request.query_params.get("async", False)
    # ac_config = request.query_params["ac_config"]
    env_id = request.query_params["env_id"]

    test_case = []
    config = None

    test_list = models.CaseSuitInfo.objects. \
        filter(case__id=pk).order_by("step").values("body", "method", "config_name")

    if project:
        project_name = models.Project.objects.get(id=project).name
        db_obj = list(models.DBConfig.objects.filter(project_id=project, env_id=env_id).values('db_name', 'db_info'))
        db_data = get_db_processor(db_obj)

    if env_id:
        env_name = models.Env.objects.get(id=env_id).name

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project=project).value

    for content in test_list:
        method = content["method"]
        config_name = content["config_name"]

        if method == "config":
            config = eval(models.Config.objects.get(name=config_name, project__id=project).body)
            continue

        elif method == "ac_config":
            ac_config = models.AccountConfig.objects.filter(project=project, ac_name=config_name).values('ac_name',
                                                                                                         'ac_info',
                                                                                                         'fixture_id').first()
            fixture_code = models.Fixture.objects.get(project=project, id=ac_config['fixture_id']).code
            ac_config['fixture_code'] = fixture_code
        else:
            body = eval(content["body"])
            test_case.append(parse_host(host, body))
    from FasterRunner.threadpool import execute
    if back_async:  # 判断是否需要异步执行，为True时异步
        tasks.async_debug_api(test_case,
                              project,
                              ac_config=ac_config,
                              name=suit_name,
                              env_name=env_name,
                              project_name=project_name,
                              db_data=db_data,
                              config=parse_host(host, config),
                              run_type=2,
                              user=request.user.username)  # delay为延时
        summary = response.TASK_RUN_SUCCESS
        return Response(summary)
    else:
        report_name = loader.debug_api(test_case,
                                       project,
                                       ac_config=ac_config,
                                       name=suit_name,
                                       env_name=env_name,
                                       project_name=project_name,
                                       db_data=db_data,
                                       config=parse_host(host, config),
                                       run_type=1,
                                       save=True,
                                       user=request.user.username)

        try:

            summary = models.Report.objects.get(name=report_name)
            response.REPORT_GET_SUCCESS['results'] = {
                "name":summary.name,
                "id":summary.id,
                "summary":eval(summary.summary),
            }
            return Response(response.REPORT_GET_SUCCESS)

        except Exception as e:

            return Response(response.REPORT_GET_FAILE)

# @api_view(["GET"])
# @accept_websocket
# @request_log(level='INFO')
def run_testsuite_pk_websocket(request, **kwargs):
    """run testsuite by pk
    kwargs为从路由中多余的参数提取出来的值，如：interface_runner/run_testsuite_pk/5/，5便是
        {
            project: int,
            name: str,
            host: str
        }
    """

    msg = request.websocket.wait()  # 接收前端发来的消息
    msg = json.loads(str(msg, encoding="utf-8"))

    pk = kwargs["pk"]

    test_list = models.CaseSuitInfo.objects. \
        filter(case__id=pk).order_by("step").values("body")

    project = msg["project"]
    suit_name = msg["suit_name"]
    host = msg["host"]  # 获取host_name
    back_async = msg.get("async", False)

    test_case = []
    config = None

    if project:
        project_name = models.Project.objects.get(id=project).name

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project=project).value

    for content in test_list:
        body = eval(content["body"])

        if "base_url" in body["request"].keys():
            config = eval(models.Config.objects.get(name=body["name"], project__id=project).body)
            continue

        test_case.append(parse_host(host, body))

    if back_async:  # 判断是否需要异步执行，为True时异步
        tasks.async_debug_api.delay(test_case, project, name=suit_name, config=parse_host(host, config))  # delay为延时
        summary = response.TASK_RUN_SUCCESS

    else:
        summary = loader.debug_api_websocket(test_case, project, project_name, name=suit_name,
                                             config=parse_host(host, config), user=request.user)
        for output in summary:
            request.websocket.send(output)

    # return Response(summary)


@api_view(['POST'])
@request_log(level='INFO')
def run_suite_tree(request):
    """run suite by tree
    {
        project: int
        relation: list
        name: str
        async: bool
        host: str
        onlyMe:bool
    }
    """
    # order by id default
    project = request.data['project']
    relation = request.data["relation"]
    back_async = request.data["async"]
    report_name = request.data["report_name"]
    host = request.data["host"]
    # config_id = request.data.get("config_id")
    env_id = request.data.get("env_id")
    only_me = request.data.get('onlyMe')
    config = None

    if project:
        project_name = models.Project.objects.get(id=project).name
        db_obj = list(models.DBConfig.objects.filter(project_id=project, env_id=env_id).values('db_name', 'db_info'))
        db_data = get_db_processor(db_obj)

    if env_id:
        env_name = models.Env.objects.get(id=env_id).name
    #
    # if config_id:
    #     # 前端有指定config，会覆盖用例本身的config
    #     config = eval(models.Config.objects.get(id=config_id).body)

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project=project).value.splitlines()

    test_sets = []
    suite_list = []
    config_list = []
    ac_config_list = []
    for relation_id in relation:
        # suite=[{'id': 5, 'suit_name': 'test1'}]
        if only_me:
            # values，里面指定获取对应键值对'id', 'suit_name'
            suite = list(models.CaseSuit.objects.filter(project__id=project,
                                                        relation=relation_id,
                                                        creator=request.user.username).order_by('id').values('id',
                                                                                                             'suit_name'))
        else:
            suite = list(models.CaseSuit.objects.filter(project__id=project,
                                                        relation=relation_id).order_by('id').values('id',
                                                                                                    'suit_name'))
        for content in suite:
            test_list = models.CaseSuitInfo.objects. \
                filter(case__id=content["id"]).order_by("step").values("body", "method", "config_name")

            testcase_list = []
            # 针对body的host和config进行处理
            for content in test_list:
                method = content["method"]
                config_name = content["config_name"]

                if method == "config":
                    config = eval(models.Config.objects.get(name=config_name, project__id=project).body)
                    config_list.append(parse_host(host, config))  # config里面的配置信息url，用host里面的的url进行映射，其实就是替换
                    continue

                elif method == "ac_config":
                    ac_config = models.AccountConfig.objects.filter(project=project, ac_name=config_name).values(
                        'ac_name',
                        'ac_info',
                        'fixture_id').first()
                    fixture_code = models.Fixture.objects.get(project=project, id=ac_config['fixture_id']).code
                    ac_config['fixture_code'] = fixture_code
                    ac_config_list.append(ac_config)
                    continue

                else:
                    body = eval(content["body"])
                    testcase_list.append(parse_host(host, body))

            # config_list=[{'name': '案场宝sit', 'request': {'base_url': 'http://fcb-sit-admin.fcb.com.cn', 'json': {}},
            #   'desc': {'header': {}, 'data': {}, 'files': {}, 'params': {}, 'variables': {}, 'parameters': {}}}]

            test_sets.append(testcase_list)  # 嵌套数组，数组里面多少个数组就多少个suit
            suite_list = suite_list + suite  # 收集suit的suit_name、id，suite_list=[{'id': 5, 'suit_name': 'test1'}, {'id': 6, 'suit_name': 'test2'}]

    if back_async:
        # tasks.async_debug_suite(test_sets,
        #                         project,
        #                         ac_config_list=ac_config_list,
        #                         report_name=report_name,
        #                         env_name=env_name,
        #                         project_name=project_name,
        #                         db_data=db_data,
        #                         config_list=config_list,
        #                         run_type=1,
        #                         save=True,
        #                         user=request.user.username)
        t = threading.Thread(target=tasks.async_debug_suite, args=(test_sets,
                                                                   project,
                                                                   ac_config_list,
                                                                   report_name,
                                                                   env_name,
                                                                   project_name,
                                                                   db_data,
                                                                   config_list,
                                                                   2,
                                                                   True,
                                                                   request.user.username))
        t.start()

        summary = loader.TEST_NOT_EXISTS
        summary["msg"] = "用例运行中，请稍后查看报告"

        return Response(summary)
    else:
        # summary = loader.debug_suite
        # t = threading.Thread(target=loader.debug_suite, args=(test_sets,
        #                                                       project,
        #                                                       ac_config_list,
        #                                                       "",
        #                                                       env_name,
        #                                                       project_name,
        #                                                       db_data,
        #                                                       config_list,
        #                                                       1,
        #                                                       True,
        #                                                       request.user.username))
        # t.start()
        report_name = loader.debug_suite(test_sets,
                                     project,
                                     ac_config_list=ac_config_list,
                                     report_name="",
                                     env_name=env_name,
                                     project_name=project_name,
                                     db_data=db_data,
                                     config_list=config_list,
                                     run_type=1,
                                     save=True,
                                     user=request.user.username)
        try:

            summary = models.Report.objects.get(name=report_name)
            response.REPORT_GET_SUCCESS['results'] = {
                "name":summary.name,
                "id":summary.id,
                "summary":eval(summary.summary),
            }
            return Response(response.REPORT_GET_SUCCESS)

        except Exception as e:

            return Response(response.REPORT_GET_FAILE)




@api_view(["POST"])
@request_log(level='INFO')
def run_test(request):
    """debug single test
    {
        host: str
        body: dict
        project :int
        config: null or dict
    }
    """

    body = request.data["body"]
    config = request.data.get("config", None)
    ac_config = request.data['ac_config']
    project = request.data["project"]
    host = request.data["host"]
    env_id = request.data['env_id']

    if host != "请选择":  # 请求头里面的域名映射
        # host=['fcb-sit-admin.fcb.com.cn']
        host = models.HostIP.objects.get(name=host, project=project).value.splitlines()

    if env_id:
        env_name = models.Env.objects.get(id=env_id).name

    if project:
        project_name = models.Project.objects.get(id=project).name
        db_obj = list(models.DBConfig.objects.filter(project_id=project, env_id=env_id).values('db_name', 'db_info'))
        db_data = get_db_processor(db_obj)

    if config:
        # 返回config表里面的每个字段的值（键值对）
        # {'name': '案场宝sit', 'request': {'base_url': 'http://fcb-sit-admin.fcb.com.cn', 'json': {}}, 'desc': {'header': {}, 'data': {}, 'files': {}, 'params': {}, 'variables': {}, 'parameters': {}}}
        config = eval(models.Config.objects.get(project=project,
                                                name=config["name"]).body)  # get方法为获取数据信息，可以使用多个键值对去数据库查询,body是以字典方式返回值

    if ac_config:
        ac_config = models.AccountConfig.objects.filter(project=project, ac_name=ac_config['ac_name']).values('ac_name',
                                                                                                              'ac_info',
                                                                                                              'fixture_id').first()
        fixture_code = models.Fixture.objects.get(project=project, id=ac_config['fixture_id']).code
        ac_config['fixture_code'] = fixture_code

    report_name = loader.debug_api(parse_host(host, loader.load_test(body)),
                                   project,
                                   project_name=project_name,
                                   name=body.get('interface_name', None),
                                   config=parse_host(host, config),
                                   ac_config=ac_config,
                                   env_name=env_name,
                                   db_data=db_data,
                                   user=request.user)  # user=request.user为获取当前用户名，比如admin

    try:

        summary = models.Report.objects.get(name=report_name)
        response.REPORT_GET_SUCCESS['results'] = {
            "name": summary.name,
            "id": summary.id,
            "summary": eval(summary.summary),
        }
        return Response(response.REPORT_GET_SUCCESS)

    except Exception as e:

        return Response(response.REPORT_GET_FAILE)
