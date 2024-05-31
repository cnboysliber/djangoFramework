import random, string
from django.db.models import Sum
from interface_runner import models
from interface_runner.utils.parser import Format
from FasterRunner.utils.celeryModel import celery_models


def get_counter(model, pk=None):
    """
    统计相关表长度
    """
    if pk:
        return model.objects.filter(project__id=pk).count()
    else:
        return model.objects.count()


def get_random_num(number=6):
    '''
    获取随机位数数字
    获取随机位数数字,string.digits只能随机10的数字，每多出10就翻倍
    :return:
    '''
    # res=''.join(random.sample(string.digits,number))
    temp_number = ""
    for count in range(0, number // 10 + 1):
        temp_number = temp_number + string.digits
    res = ''.join(random.sample(temp_number, number))
    return res


def get_db_processor(data: list):
    res_dict = {}
    for valueDict in data:
        res_dict.update({valueDict['db_name']: eval(valueDict['db_info'])})
    return res_dict


def report_status_count(pk):
    query_set = models.Report.objects.filter(project__id=pk)
    report_fail = query_set.filter(status=0).count()
    report_success = query_set.filter(status=1).count()
    return report_fail, report_success


def get_project_detail(pk):
    """
    项目详细统计信息
    """
    api_count = get_counter(models.API, pk=pk)
    case_count = get_counter(models.CaseSuit, pk=pk)
    config_count = get_counter(models.Config, pk=pk)
    variables_count = get_counter(models.Variables, pk=pk)
    report_count = get_counter(models.Report, pk=pk)
    report_fail, report_success = report_status_count(pk=pk)
    host_count = get_counter(models.HostIP, pk=pk)
    # plan_count = get_counter(models.Plan, pk=pk)
    task_query_set = celery_models.PeriodicTask.objects.filter(description=pk)
    task_count = task_query_set.count()
    case_id = []
    task_query_set = task_query_set.filter(enabled=1).values("args")
    for i in task_query_set:
        case_id += eval(i.get('args'))
    case_step_count = models.CaseSuit.objects.filter(pk__in=case_id).aggregate(Sum("case_count"))

    return {
        "api_count": api_count,
        "case_count": case_count,
        "task_count": task_count,
        "config_count": config_count,
        "variables_count": variables_count,
        "report_count": report_count,
        "report_fail": report_fail,
        "report_success": report_success,
        "host_count": host_count,
        # "case_step_count": case_step_count.get("length__sum"),
        "case_step_count": case_step_count.get("case_count__sum"),
    }


def project_init(project):
    """
    新建项目初始化
    """

    # 自动生成默认debugtalk.py
    models.Debugtalk.objects.create(project=project)
    # 自动生成API tree
    models.Relation.objects.create(project=project)
    # 自动生成Test Tree
    models.Relation.objects.create(project=project, type=2)


def project_end(project):
    """
    删除项目相关表 filter不会报异常 最好不用get
    """
    models.Debugtalk.objects.filter(project=project).delete()
    models.Config.objects.filter(project=project).delete()
    models.API.objects.filter(project=project).delete()
    models.Relation.objects.filter(project=project).delete()
    models.Report.objects.filter(project=project).delete()
    models.Variables.objects.filter(project=project).delete()
    celery_models.PeriodicTask.objects.filter(description=project).delete()

    case = models.Case.objects.filter(project=project).values_list('id')

    for case_id in case:
        models.CaseSuitInfo.objects.filter(case__id=case_id).delete()


def tree_end(params, project):
    """
    project: Project Model
    params: {
        node: int,
        type: int
    }
    """
    type = params['type']
    node = params['node']

    if type == 1:
        models.API.objects. \
            filter(relation=node, project=project).delete()

    # remove node testcase
    elif type == 2:
        case = models.CaseSuit.objects. \
            filter(relation=node, project=project).values('id')

        for case_id in case:
            models.CaseSuitInfo.objects.filter(case__id=case_id['id']).delete()
            models.CaseSuit.objects.filter(id=case_id['id']).delete()


def update_Case_suit_info(body, case, project, env_id, username):
    step_list = list(models.CaseSuitInfo.objects.filter(case=case).values('id'))

    for index in range(len(body)):
        test = body[index]
        try:
            # 修改用例后，会走这个逻辑
            format_http = Format(test['newBody'])
            format_http.parse()
            case_name = format_http.interface_name
            config_name = None
            new_body = format_http.testcase
            interface_path = format_http.interface_path
            method = format_http.method
            source_api_id = test.get('source_api_id', 0)
            if source_api_id == 0:
                source_api_id = test['id']

        except KeyError:
            if test["body"]["method"] == "config":

                new_body = models.Config.objects.get(name=test['body']['name'], project_id=project, env_id=env_id).body
                config_name = test['body']['name']
                case_name = None
                interface_path = None
                method = "config"
                # config没有source_api_id,默认为0
                source_api_id = 0
                index = 0
            elif test['body']['method'] == 'ac_config':

                ac_info = models.AccountConfig.objects.filter(ac_name=test['body']['ac_name'], project_id=project,
                                                              env_id=env_id).values("ac_info", "description", "id",
                                                                                    "fixture_id")
                new_body = {
                    "ac_name": test['body']['ac_name'],
                    "request": ac_info[0],
                }
                config_name = test['body']['ac_name']
                case_name = None
                interface_path = None
                method = "ac_config"
                # config没有source_api_id,默认为0
                source_api_id = 0
                index = 0
            else:
                if "case_id" in test.keys():  # 新增用例时，是没有case_id的
                    case_step = models.CaseSuitInfo.objects.get(id=test['id'])  # 原来的用例，走这逻辑
                else:
                    # 新增用例时，test['id']的id为API里面的主键id
                    case_step = models.API.objects.get(id=test['id'])

                new_body = case_step.body
                case_name = test['body']['interface_name']
                config_name = None
                interface_path = test['body']['interface_path']
                method = test['body']['method']
                source_api_id = test.get('source_api_id', 0)
                # 新增的case没有source_api_id字段,需要重新赋值
                if source_api_id == 0:
                    source_api_id = test['id']

            # new_body = eval(case_step.body)

            # if "name" in eval(case_step.body).keys():
            #     if case_step.name != name:
            #         new_body['name'] = name
            #
            # if "interface_name" in eval(case_step.body).keys():
            #     if case_step.case_name != name:
            #         new_body['interface_name'] = name
        if 'case_id' in test.keys():
            case_id = test['case_id']

        kwargs = {
            "case_name": case_name,
            "config_name": config_name,
            "body": new_body,
            "interface_path": interface_path,
            "method": method,
            "step": index,
            "source_api_id": source_api_id,
            "case_id": case_id,
            "env_id": env_id,
        }

        if 'config' not in test['body']['method']:
            if 'case_id' in test.keys():  # 根据用例id判断去更新对象，只针对非config对象
                models.CaseSuitInfo.objects.filter(id=test['id']).update(**kwargs, updater=username)
                step_list.remove({"id": test['id']})
            else:
                kwargs['case_name'] = case
                models.CaseSuitInfo.objects.create(**kwargs, creator=username)

    #  去掉多余的step
    for content in step_list:
        models.CaseSuitInfo.objects.filter(id=content['id']).delete()


def generate_case_suit_info(body, case, env_id, username):
    """
    生成用例集步骤
    [{
        id: int,
        project: int,
        name: str,
        method: str,
        url: str
    }]

    """
    #  index也是case step的执行顺序
    case_steps: list = []
    index_step = 0
    for index in range(len(body)):
        test = body[index]

        try:
            format_http = Format(test['newBody'])
            format_http.parse()
            interface_name = format_http.interface_name
            new_body = format_http.testcase
            interface_path = format_http.interface_path
            method = format_http.method
            config_name = None
            source_api_id = test.get('source_api_id', 0)
            if source_api_id == 0:  # 新增用例时，不存在source_api_id字段，所以默认为0，这时候test['id']的id为API里面的主键id
                source_api_id = test['id']
            index_step = index_step + 1
        except KeyError:
            if test["body"]["method"] == "config":
                config_name = test["body"]["name"]
                interface_name = None
                interface_path = None
                method = test["body"]["method"]
                config = models.Config.objects.get(name=config_name)
                new_body = eval(config.body)
                source_api_id = 0  # config没有api,默认为0
                index_step = 0
            elif test['body']['method'] == 'ac_config':
                config_name = test["body"]["ac_name"]
                interface_name = None
                interface_path = None
                method = test["body"]["method"]
                config = models.AccountConfig.objects.filter(ac_name=config_name).values('ac_name', 'ac_info',
                                                                                         'description', 'id',
                                                                                         'fixture_id').first()
                ac_name = config['ac_name']
                del config['ac_name']
                new_body = {
                    'ac_name': ac_name,
                    'request': config,
                }
                source_api_id = 0  # config没有api,默认为0
                index_step = 0
            else:
                api = models.API.objects.get(id=test['id'])
                new_body = eval(api.body)
                interface_name = test['body']['interface_name']
                config_name = None

                if api.interface_name != interface_name:
                    new_body['interface_name'] = interface_name

                interface_path = test['body']['interface_path']
                method = test['body']['method']
                source_api_id = test['id']
                index_step = index_step + 1

        kwargs = {
            "case_name": interface_name,
            "config_name": config_name,
            "body": new_body,
            "interface_path": interface_path,
            "method": method,
            "step": index_step,
            "case": case,  # 就是case_id
            "source_api_id": source_api_id,
            "creator": username,
            "env_id": env_id
        }
        case_step = models.CaseSuitInfo(**kwargs)
        case_steps.append(case_step)
    models.CaseSuitInfo.objects.bulk_create(objs=case_steps)


def case_end(pk):
    """
    pk: int case id
    """
    # models.CaseSuitInfo.objects.filter(case__id=pk).delete()
    if isinstance(pk, int):
        models.CaseSuit.objects.filter(id=pk).delete()
    elif isinstance(pk, list):
        models.CaseSuit.objects.filter(id__in=pk).delete()
    else:
        return


class CaseProcessor:
    '''
    针对接口信息进行处理，提供给接口自动化测试框架使用
    data=[
  {
    "interface_name": "获取用户项目列表",
    "rig_id": "None",
    "times": 1,
    "request": {
      "interface_path": "/hdb-scene-server/appapi/v1/queryProjectListByUserId",
      "method": "POST",
      "verify": True,
      "header": {
        "Content-Type": "application/json; charset\u003dutf-8",
        "token": "${ut}",
        "brokerId": "${userId}",
        "sign": "${sign}",
        "timestamp": "${timestamp}",
        "terminalType": "Android"
      },
      "json": {
        "userId": "${userId}"
      }
    },
    "desc": {
      "header": {
        "Content-Type": "",
        "token": "",
        "brokerId": "",
        "sign": "",
        "timestamp": "",
        "terminalType": ""
      },
      "data": {},
      "files": {},
      "params": {},
      "variables": {},
      "auto_product": {
        "num_3": "",
        "num_6": ""
      },
      "save": {
        "code": "",
        "save1": ""
      }
    },
    "save": [
      {
        "code": "$..\u0027code\u0027"
      },
      {
        "save1": "$..\u0027code\u0027"
      }
    ],
    "assert": [
      {
        "in": [
          "000000",
          "$..\u0027code"
        ]
      },
      {
        "in": [
          "111111",
          "$..\u0027code"
        ]
      }
    ],
    "auto_product": [
      {
        "num_3": "get_random_num(3)"
      },
      {
        "num_6": "get_random_num(6)"
      }
    ]
  }
]
    '''

    def __init__(self):
        pass

    def case_info_add(self, data: dict, key: str,joint_tag='=') -> str:
        '''
        针对key=value的数据，进行拼接，提供给接口自动化框架使用
        :param data:
        :param key:
        :return:
        '''
        if key in data.keys():
            res = ''
            for dataValue in data[key]:
                for key, value in dataValue.items():
                    if res == '':
                        res = ''.join((key, joint_tag, value))
                    else:
                        res = ''.join((res, ";", key, joint_tag, value))

            return res


    def switch_str(self, obj):
        if isinstance(obj, str):
            obj = f"'{obj}'"
        else:
            obj=str(obj)
        return obj

    def assert_case_info_processor(self, data: dict, key) -> str:
        '''
        assert拼接，提供给接口自动化框架使用
        :return:
        '''
        res = ''
        if key in data.keys():
            for assertValue in data[key]:
                for as_key, as_value in assertValue.items():
                    if res == '':
                        res = ''.join((self.switch_str(as_value[0]), as_key, as_value[1]))
                    else:
                        res = ''.join((res, ';', self.switch_str(as_value[0]), as_key, as_value[1]))

            return res

    def case_info_processor(self, all_data: list) -> dict:
        '''
        针对接口框架传来的参数，进行重组，提供给接口自动化框架使用
        '''
        case_list = []
        for data in all_data:
            headers = str(data["request"]["header"])
            body = str(data["request"]["json"])

            auto_product = self.case_info_add(data, "auto_product",joint_tag='=')
            before_sql = self.case_info_add(data, "before_sql",joint_tag=':')
            execute_sql = self.case_info_add(data, "execute_sql",joint_tag=':')
            expect_sql_result = self.case_info_add(data, "auto_product",joint_tag=':')

            save = self.case_info_add(data, "save")
            assertValue = self.assert_case_info_processor(data, "assert")

            case_dict = {
                "caseid": 1,
                "priority": "P0",
                "module": "暂未支持该功能",
                "interfacePath": data["request"]["interface_path"],
                "interfaceName": data["interface_name"],
                "method": data["request"]["method"],
                "description": "暂未支持该功能",
                "headers": headers,
                "body": body,
                "autoProduct": auto_product,
                "save": save,
                "assert": assertValue,
                "beforeSql": before_sql,
                "executeSql": execute_sql,
                "expectSqlResult": expect_sql_result,
                "count": data["times"],
                "product": "scene_bao",
                "owner": "",
                "loginTag": [
                    "bro"
                ],
                "excelPath": None,
                "excelSheet": None
            }

            case_list.append(case_dict)

        return case_list
