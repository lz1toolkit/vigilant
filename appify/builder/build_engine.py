import importlib
import os
import traceback

from appify.builder.objects import (
    BuildResult, BuildException
)
from appify.builder import field_keys
from appify.builder.config import BASIC_CONFIG, BuildConfig


DEFAULT_BUILD_PATH = os.path.join(os.getcwd(), 'build')


class BuildEngine:

    def __init__(self, path=None):
        self.build_path = path if path is not None else DEFAULT_BUILD_PATH

    @staticmethod
    def find_script(name):
        try:
            scripts_module = importlib.import_module('appify.builder.scripts.' + name)
        except ModuleNotFoundError as e:
            print('BuildEngine find_script: cannot find the module. e = ' + str(e))
            return None

        return scripts_module

    @staticmethod
    def find_method(scripts_module, name):
        func = getattr(scripts_module, name, None)
        if not callable(func):
            func = None
        return func

    def real_build(
            self, name: str, fingerprint: str, build_info,
            mth_build, mth_get_config
    ):
        build_workspace = os.path.join(self.build_path, name, fingerprint)
        os.makedirs(build_workspace)

        task_config = {} if not mth_get_config else mth_get_config()
        task_config[field_keys.BUILD_WORKSPACE] = build_workspace
        task_config[field_keys.BUILD_INFO] = build_info
        task_config[field_keys.APK_INFO] = {}

        try:
            config: BuildConfig = BuildConfig(BASIC_CONFIG, task_config, mth_get_config())
            return mth_build(config)
        except (BuildException, Exception):
            msg = 'Build Failed: script_name=%s, build_info=%s, err=%s' % (
                name, str(build_info), traceback.format_exc())
            return BuildResult(False, msg, None)

    def build(self, name: str, fingerprint: str, build_info) -> BuildResult:

        script_module = self.find_script(name)

        return self.real_build(
            name,
            fingerprint,
            build_info,
            self.find_method(script_module, 'build_apk'),
            self.find_method(script_module, 'get_config'),
        )

