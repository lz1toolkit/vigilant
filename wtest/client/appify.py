import os
import traceback

import requests
import typing

FIELD_APP_NAME = 'name'
FIELD_APP_WM = 'wm'
FIELD_BRANCH = 'branch'
FIELD_FROM_VALUE = 'from_val'
FIELD_APP_ADDRESS = 'address'
FIELD_FILE_PATH_MAP = 'file_path_map'
FIELD_EXTRA = 'extra'


class ApkInfo:

    @staticmethod
    def from_json(data):
        if not data:
            return None

        try:
            return ApkInfo(
                name=data[FIELD_APP_NAME],
                wm=data[FIELD_APP_WM],
                from_val=data[FIELD_FROM_VALUE],
                branch=data[FIELD_BRANCH],
                address=data[FIELD_APP_ADDRESS],
                file_path_map=data[FIELD_FILE_PATH_MAP],
                extra=data[FIELD_EXTRA]
            )
        except:
            traceback.print_exc()
            return None

    def __init__(
            self,
            name='',
            wm='',
            from_val='',
            branch='',
            address='',
            file_path_map=None,
            extra=None
    ):
        self.name = name
        self.wm = wm
        self.from_val = from_val
        self.branch = branch
        self.address = address
        self.file_path_map = file_path_map
        self.extra = extra


class Appify:

    def __init__(self, base_url):
        self.base_url = base_url

    def apk_map(self,
                build_name,
                hours=24,
                count=1,
                status=1
                ) -> typing.Dict[str, ApkInfo]:
        url = self.base_url + '/apk'
        params = {
            'build_name': build_name,
            'hours': hours,
            'count': count,
            'status': status
        }
        try:
            content = requests.get(url, params).json()['data']
            result = {}
            for key in content:
                result[key] = ApkInfo.from_json(content[key])
            return result
        except Exception as e:
            traceback.print_exc()
            return None

    def download(self, name, path, dest_path):
        url = self.base_url + '/download?name=%s&path=%s' % (name, path)
        resp = requests.get(url)
        with open(dest_path, 'wb') as f:
            f.write(resp.content)
