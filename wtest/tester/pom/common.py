import os
import time
import traceback
import subprocess

import uiautomator2

from base import log
from wtest.tester.pom.logcat import Logcat
from wtest.tester import field_keys

FILE_PATH = os.path.dirname(__file__)
FAST_BOT_PATH = os.getenv(field_keys.FASTBOT_PATH)


class TestException(Exception):

    def __int__(self, msg):
        self.msg = msg


class ViewSelector:

    def __init__(self, text=None, resource_id=None):
        self.text = text
        self.resource_id = resource_id

    def __str__(self):
        return '{text = %s, resource = %s}' % (str(self.text), str(self.resource_id))


class Driver:

    def connect(self):
        pass

    def disconnect(self):
        pass

    def finish(self):
        pass

    def install(self, path):
        pass

    def uninstall(self, pkg):
        pass

    def click(self, selector: ViewSelector):
        pass

    def exists(self, selector: ViewSelector):
        pass

    def ergodic_prepare(self, abl_stings_file):
        pass

    def ergodic(self, pkg, minutes=10):
        pass

    def stop(self, pkg):
        pass

    def scheme(self, scheme):
        pass

    def auto_swipe(self):
        pass

    def wake_up(self):
        pass

    def view(self, selector):
        pass

    @staticmethod
    def adb(cmd, get_return=False):
        if not get_return:
            os.system(cmd)
            return ''
        else:
            ex = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            out, err = ex.communicate()
            if not err:
                status = ex.wait()
                if status == 0:
                    content = out.decode().strip()
                    return content
            return ''


class Workspace:
    def __init__(self, root):
        self.workspace = root

        self.root_apk_dir = os.path.join(self.workspace, 'apk')
        os.mkdir(self.root_apk_dir)

        self.root_dev_dir = os.path.join(self.workspace, 'dev')
        os.mkdir(self.root_dev_dir)

        self.apk_dir_map = {}
        self.dev_dir_map = {}

    def add_apk_dir(self, name):
        p = os.path.join(self.root_apk_dir, name)
        os.mkdir(p)
        self.apk_dir_map[name] = p

    def get_apk_dir(self, name):
        return self.apk_dir_map[name]

    def add_dev_dir(self, dev_name):
        p = os.path.join(self.root_dev_dir, dev_name)
        os.mkdir(p)
        self.dev_dir_map[dev_name] = p

    def apk_path(self, name):
        if name in self.apk_dir_map:
            return os.path.join(self.apk_dir_map[name], '%s.apk' % name)
        return None

    def apk_file_path(self, apk_name, file_name):
        if apk_name in self.apk_dir_map:
            return os.path.join(self.apk_dir_map[apk_name], file_name)
        return None

    def dev_file_path(self, dev_name, *file_path):
        if dev_name in self.dev_dir_map:
            return os.path.join(self.dev_dir_map[dev_name], *file_path)
        return None


class App:
    __TAG = 'App'

    def __init__(self, pkg, serial, driver: Driver, workspace: Workspace):
        self.pkg = pkg
        self.serial = serial
        self.driver = driver
        self.driver.connect()
        self.workspace = workspace

    def install(self, apk_name):
        if not self.workspace:
            log.e(App.__TAG, 'workspace is None')
            raise TestException('Error: workspace is None')

        path = self.workspace.apk_path(apk_name)
        if not path:
            log.w(App.__TAG, 'apk path is None')
            return

        if not os.path.exists(path):
            log.e(App.__TAG, 'path is not exists; path = %s' % path)
            return TestException('')

        log.d(App.__TAG, ' install app; serial = %s, path = %s' % (self.serial, path))
        self.driver.install(path)

    def uninstall(self):
        log.d(App.__TAG, 'uninstall app; serial = %s, pkg = %s' % (self.serial, self.pkg))
        self.driver.uninstall(self.pkg)

    def launch(self):
        pass

    def stop(self):
        log.d(App.__TAG, 'force-stop app; serial = %s, pkg = %s' % (self.serial, self.pkg))
        self.driver.stop(self.pkg)

    def logcat(self, start_date=None, grep=None):
        cmd = 'adb -s %s logcat' % self.serial
        if start_date:
            cmd = cmd + ' -t "%s"' % start_date
        if grep:
            cmd = cmd + ' | ' + grep
        log.d(App.__TAG, 'logcat; cmd = %s' % cmd)
        return Logcat(cmd)


class Page:

    def __init__(self, app: App):
        self.app = app
        self.driver: Driver = app.driver


class Activity(Page):

    def __init__(self, app: App, name: str):
        super().__init__(app)
        self.name = name

    def is_resume(self, retry_count=6) -> bool:

        count = 0

        while count < retry_count:
            cmd = ('adb -s %s shell dumpsys activity activities | grep mResumedActivity'
                   % self.app.serial)
            ret = self.driver.adb(cmd, get_return=True)
            log.d(self.name, 'dumpsys activity activities | grep mResumedActivity -> ' + ret)
            b = self.name in ret
            if b:
                return True
            else:
                count = count + 1

            time.sleep(10)

        return False


def perform_wait(v, func) -> bool:
    retry_count = 120
    while True and retry_count > 0:
        if v.exists(timeout=2):
            func(v)
            return True
        else:
            print('view 不存在')
            retry_count = retry_count - 1
        time.sleep(2)
    return False


class DefaultDriver(Driver):
    __TAG = 'NormalDriver'

    def __init__(self, serial):
        self.serial = serial
        self.u2 = None
        # Fastbot: Activity黑名单配置（黑名单内的activity不覆盖）
        self.abl_string_file = None

    def connect(self):
        os.system(
            "adb -s %s shell ps -df | grep uiautomator | grep -v grep | awk '{ print $2 }' | xargs kill" % self.serial)
        try:
            self.u2 = uiautomator2.connect(self.serial)
        except Exception:
            err = traceback.format_exc()
            err = 'serial = %s; %s' % (self.serial, err)
            log.e(DefaultDriver.__TAG, err)
            raise TestException(err)

    def disconnect(self):
        if self.u2 and self.u2.uiautomator.running():
            self.u2.uiautomator.stop()

    def install(self, path):
        os.system('adb -s %s install %s' % (self.serial, path))

    def uninstall(self, pkg):
        os.system('adb -s %s uninstall %s' % (self.serial, pkg))
        os.system('adb -s %s shell pm clear %s' % (self.serial, pkg))

    def click(self, selector: ViewSelector):
        v = None
        if selector.resource_id:
            v = self.u2(resourceId=selector.resource_id)
        elif selector.text:
            v = self.u2(text=selector.text)
        else:
            return False
        return perform_wait(v, lambda view: view.click())

    def view(self, selector: ViewSelector):
        v = None
        if selector.resource_id:
            v = self.u2(resourceId=selector.resource_id)
        elif selector.text:
            v = self.u2(text=selector.text)
        else:
            return None
        if perform_wait(v, lambda _: print('view exists')):
            return v
        else:
            return None

    def exists(self, selector: ViewSelector):
        v = None
        if selector.resource_id:
            v = self.u2(resourceId=selector.resource_id)
        elif selector.text:
            v = self.u2(text=selector.text)
        else:
            return False
        return perform_wait(v, lambda _: print('view exists'))

    def ergodic_prepare(self, abl_stings_file):
        os.system('adb -s %s push %s/*.jar /sdcard' % (self.serial, FAST_BOT_PATH))
        os.system('adb -s %s push %s/libs/* /data/local/tmp/' % (self.serial, FAST_BOT_PATH))
        if abl_stings_file and os.path.exists(abl_stings_file):
            log.d(DefaultDriver.__TAG, 'abl_stings_file = %s' % abl_stings_file)
            self.abl_string_file = abl_stings_file
            os.system('adb -s %s push %s /sdcard' % (self.serial, self.abl_string_file))

    def ergodic(self, pkg, minutes=10):
        if not self.abl_string_file:
            os.system(
                'adb -s %s shell CLASSPATH=/sdcard/monkeyq.jar:/sdcard/framework.jar:/sdcard/fastbot-thirdpart.jar exec app_process /system/bin com.android.commands.monkey.Monkey -p %s --agent reuseq --running-minutes %d --throttle 1000 -v -v' % (
                    self.serial, pkg, minutes))
        else:
            os.system(
                'adb -s %s shell CLASSPATH=/sdcard/monkeyq.jar:/sdcard/framework.jar:/sdcard/fastbot-thirdpart.jar exec app_process /system/bin com.android.commands.monkey.Monkey -p %s --agent reuseq --running-minutes %d --act-blacklist-file /sdcard/abl.strings --throttle 1000 -v -v' % (
                    self.serial, pkg, minutes))

    def stop(self, pkg):
        os.system('adb -s %s shell am force-stop %s' % (self.serial, pkg))

    def auto_swipe(self):
        screen_width, screen_height = self.u2.window_size()
        x = screen_width / 2
        sy = screen_height - 50
        ey = screen_width + 50
        os.system('adb -s %s shell input swipe %d %d %d %d' % (self.serial, x, sy, x, ey))

    def scheme(self, scheme):
        if not scheme:
            return
        os.system('adb -s %s shell am start "%s"' % (self.serial, scheme))

    def wake_up(self):
        # 唤醒屏幕进入桌面
        cmd = 'adb -s %s shell "dumpsys deviceidle | grep mScreenOn"' % self.serial
        ex = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out, err = ex.communicate()
        if not err:
            status = ex.wait()
            if status == 0:
                content = out.decode().strip()
                if 'mScreenOn=false' in content:
                    # 当前熄屏
                    os.system('adb -s %s shell input keyevent 26' % self.serial)
                    os.system('adb -s %s shell input swipe 200 800 200 0' % self.serial)
                    os.system('adb -s %s shell input swipe 200 1500 200 0' % self.serial)
