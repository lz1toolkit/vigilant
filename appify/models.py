import json
from enum import Enum
from datetime import datetime

import django.utils.timezone
from django.db import models


# Create your models here.

def get_value(data, key, default):
    if key in data:
        return data[key]
    else:
        return default


class TaskStatus(Enum):
    FAILURE = -1
    CREATION = 0
    SUCCESS = 1


class BuildTask(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    fingerprint = models.CharField(db_index=True, max_length=50, default="")
    # 构建信息
    build_info = models.CharField(max_length=200, null=False)
    # 构建补充描述
    build_des = models.CharField(max_length=100, null=False)
    # 构建后的应用信息
    apk_info = models.CharField(max_length=500, null=False)
    create_time = models.DateTimeField(db_index=True, default=django.utils.timezone.now)
    start_time = models.DateTimeField(db_index=True, default=django.utils.timezone.now)
    end_time = models.DateTimeField(db_index=True, auto_now=True)
    status = models.IntegerField(default=TaskStatus.CREATION.value)

    def __str__(self):
        return 'name = %s, build_info = %s, status = %d, build_des = %s, apk_info = %s' % (
            self.name, self.build_info, self.status, self.build_des, self.apk_info)

    @staticmethod
    def from_data(data):
        task = BuildTask()

        task.name = get_value(data, 'name', 'daily_apk')
        task.fingerprint = get_value(data, 'fingerprint', str(int(datetime.now().timestamp())))
        task.build_info = json.dumps(get_value(data, 'build_info', {}))
        task.build_des = json.dumps(get_value(data, 'build_des', {}))
        task.status = TaskStatus.CREATION.value

        return task
