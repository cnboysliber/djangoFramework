# -*- coding:utf-8 -*-
import json
import logging
import traceback
from collections import Iterable


logger = logging.getLogger('django')


def format_json(value):
    try:
        return json.dumps(value, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.warning(e)
        return value


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



