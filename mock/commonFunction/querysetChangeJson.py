import re
import json
import traceback
from collections import Iterable
from django.core import serializers


def queryset_change_json(querylist, ):
    dict_queryset_list = {}
    arr_json_list = []

    dict_queryset_list['list'] = json.loads(serializers.serialize("json", querylist))
    for i in dict_queryset_list['list']:
        arr_json_list.append(dict(i['fields'], **{'id': i['pk']}))

    return arr_json_list


def obj_to_dict(obj, filters=None):
    if not obj:
        return {}
    out = dict()
    try:
        for k, v in obj.__dict__.items():
            if k.startswith('_') or k in ['query', 'query_class']:
                continue
            elif not filters or (filters and k in filters):
                out[k] = v
    except AttributeError:
        out = dict(zip(obj.keys(), obj))
    except Exception:
        print(traceback.format_exc())

    return out


def obj_to_dicts(obj, filters=None):
    if obj is None:
        return []
    if isinstance(obj, Iterable):
        rv = list()
        for _ in obj:
            rv.append(obj_to_dict(_, filters=filters))
    else:
        raise Exception('%s is not Iterable' % type(obj))

    return rv
