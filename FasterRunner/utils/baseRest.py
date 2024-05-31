from __future__ import absolute_import
import json
import requests
import urllib.parse

import performApp.utils.error
from FasterRunner.utils import baseError as err

HTTP_GET = 'GET'
HTTP_POST = 'POST'
HTTP_PUT = 'PUT'
HTTP_DELETE = 'DELETE'


class RestRequest(object):
    def __init__(self, host, json_encode=True):
        self.host = host
        self.resp = None
        self.json_encode = json_encode

    def get_url(self, uri):
        return urllib.parse.urljoin(self.host, uri)

    def _fetch(self, uri, method, headers=None, timeout=10, file=None, **data):
        url = self.get_url(uri)

        if headers is None:
            headers = dict()

        if method == HTTP_GET:
            print(url, data, headers)
            resp = requests.get(url, headers=headers, **data, timeout=timeout)
        elif method == HTTP_POST or method == HTTP_PUT:
            if self.json_encode:
                headers['Content-Type'] = 'application/json'
                data = json.dumps(data)

            if method == HTTP_POST:
                print(url, data, headers)
                if headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                    resp = requests.post(url, urllib.parse.urlencode(data), headers=headers,
                                         allow_redirects=True, verify=False,
                                         timeout=timeout)
                else:
                    resp = requests.post(url, data=data, headers=headers,
                                         allow_redirects=True, verify=False,
                                         timeout=timeout, files=file)
            else:
                resp = requests.put(url, data=data, headers=headers,
                                    allow_redirects=True, verify=False, files=file)
        elif method == HTTP_DELETE:
            resp = requests.delete(url, headers=headers, allow_redirects=True,
                                   verify=False)
        else:
            raise Exception('Unsupported method[%s]' % method)

        self.resp = resp

    def fetch(self, uri, method='GET', headers=None, file=None, **data):
        try:
            self._fetch(uri, method, headers, file=file, **data)
        except ConnectionError:
            raise performApp.utils.error.ErrInternalRequest

    @property
    def ok(self):
        return self.resp.status_code == 200

    @property
    def data(self):
        return self.resp.json()

    @property
    def content(self):
        return self.resp.content

    @property
    def status_code(self):
        return self.resp.status_code


