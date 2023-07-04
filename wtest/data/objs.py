import json

import yaml


class JSONObject:
    def __init__(self, d):
        self.__dict__ = d


class DefaultReader:

    @staticmethod
    def from_txt(path: str):
        with open(path, mode="r", encoding="utf-8") as f:
            content = f.read()
            return json.loads(content, object_hook=JSONObject)

    @staticmethod
    def from_json(path: str):
        with open(path, mode="r", encoding="utf-8") as f:
            content = f.read()
            return json.loads(content, object_hook=JSONObject)

    @staticmethod
    def from_yaml(path: str):
        with open(path, mode="r", encoding="utf-8") as f:
            content = f.read()
            return yaml.safe_load(content)

    def __call__(self, path):
        if path is None:
            return None

        name_format = []
        if "." in path:
            name_format = path.split(".")

        if len(name_format) != 2:
            return None

        func_name = "from_" + name_format[1]
        fc = getattr(DefaultReader, func_name, None)
        if callable(fc):
            return fc(path)
        else:
            print("Warning: cannot find the func for %s" % func_name)
            return None


def file(path: str, reader=None):
    if path is None:
        print("Param error: path is None.")

    if reader is None:
        reader = DefaultReader()

    return reader(path)
