import importlib
import os

from wtest.tester import field_keys

DEFAULT_BUILD_PATH = os.path.join(os.getcwd(), 'build')


class TestEngine:

    def __init__(self, name, fingerprint, path=None):
        self.test_name = name
        self.fingerprint = fingerprint
        self.build_path = path if path is not None else DEFAULT_BUILD_PATH
        self.workspace = os.path.join(self.build_path, name, fingerprint)

    def __enter__(self):
        path = os.path.join(self.build_path, self.workspace)
        if not os.path.exists(path):
            os.makedirs(path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def find_script(name):
        try:
            scripts_module = importlib.import_module('wtest.tester.scripts.' + name)
        except ModuleNotFoundError as e:
            print('TestEngine find_script: cannot find the module. e = ' + str(e))
            return None

        return scripts_module

    def test(self, ctx: {}):
        ctx[field_keys.TEST_WORKSPACE] = self.workspace

        script_module = self.find_script(self.test_name)

        func_test = getattr(script_module, 'test', None)
        if not callable(func_test):
            func_test = None

        func_prepare_test = getattr(script_module, 'prepare_test', None)
        if not callable(func_prepare_test):
            func_prepare_test = None

        if not func_test or not func_prepare_test:
            return False, {}

        test_data = func_prepare_test(ctx)

        ctx[field_keys.TEST_DATA] = test_data
        return func_test(ctx)

