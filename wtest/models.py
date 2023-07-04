import json
from enum import Enum

from django.utils import timezone
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
    RUNNING = 1
    SUCCESS = 2


class TestTask(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=False)
    status = models.IntegerField(default=TaskStatus.CREATION.value)
    test_info = models.CharField(max_length=500, null=False)
    create_time = models.DateTimeField(db_index=True, default=timezone.now)
    start_time = models.DateTimeField(db_index=True, default=timezone.now)
    end_time = models.DateTimeField(db_index=True, auto_now=True)

    @staticmethod
    def from_data(data):
        task = TestTask()

        task.name = get_value(data, 'name', '')
        task.test_info = json.dumps(get_value(data, 'test_info', {}))

        return task
