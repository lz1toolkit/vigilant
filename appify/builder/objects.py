import typing


class BuildException(Exception):

    def __init__(self, msg):
        self.msg = msg


class Apk:

    def __init__(self,
                 name,
                 wm,
                 from_val,
                 address,
                 branch,
                 file_path_map,
                 extra
                 ):
        self.name = name
        self.address = address
        self.wm = wm
        self.from_val = from_val
        self.branch = branch
        self.file_path_map = file_path_map
        self.extra = extra

    def to_dict(self):
        return {
            'name': self.name,
            'wm': self.wm,
            'from_val': self.from_val,
            'address': self.address,
            'branch': self.branch,
            'file_path_map': self.file_path_map,
            'extra': self.extra
        }


class BuildResult:

    def __init__(self,
                 result: bool,
                 msg: str,
                 apk_info):
        self.result = result
        self.msg = msg
        self.apk_info: typing.Dict[str, Apk] = apk_info
