import os
from collections import defaultdict

from appify.builder import field_keys

BASIC_CONFIG = {
    field_keys.ANDROID_SDK_PATH: os.getenv('APPLIFY_ANDROID_SDK'),
    field_keys.ANDROID_NDK_PATH: os.getenv('APPLIFY_ANDROID_NDK'),
    field_keys.BUILD_PROJECT_PATH: os.getenv('APPLIFY_BUILD_PROJECT_PATH'),
    field_keys.OPTION_BUILD_TYPE: "release",
    field_keys.OPTION_BUILD_BRANCH: 'master'
}


class BuildConfig:

    def __init__(self, basic_config=None, task_config=None, apk_config=None):
        tmp = defaultdict(lambda: None)
        if basic_config and isinstance(basic_config, dict):
            tmp.update(basic_config)
        self.basic_config = tmp

        tmp = defaultdict(lambda: None)
        if task_config and isinstance(task_config, dict):
            tmp.update(task_config)
        self.task_config = tmp

        tmp = defaultdict(lambda: None)
        if apk_config and isinstance(apk_config, dict):
            tmp.update(apk_config)
        self.apk_config = tmp

        self.build_config = defaultdict(lambda: None)

    def get(self, name):
        c_list = [self.build_config, self.apk_config, self.task_config, self.basic_config]
        for c in c_list:
            if c and name in c and c[name]:
                return c[name]
        return None

    def set(self, name, value):
        self.build_config[name] = value

    def __str__(self):
        return 'basic_config=%s, task_config=%s' % (str(self.basic_config), str(self.task_config))
