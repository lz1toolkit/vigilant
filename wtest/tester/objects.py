import os


class Device:

    def __init__(self, serial):
        self.serial = serial

    def pull(self, source, dest):
        if not source or not dest:
            return

        os.system('adb -s %s pull %s %s' % (self.serial, source, dest))

    def rm(self, path):
        if not path:
            return

        os.system('adb -s %s shell rm -rf %s' % (self.serial, path))
