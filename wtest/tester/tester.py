import json
import os
from collections import defaultdict
from json import JSONDecodeError
from datetime import datetime

from wtest.models import TestTask, TaskStatus
from wtest.tester.test_engine import TestEngine
from wtest.client.appify import Appify
from wtest.client import mail
from wtest.tester import field_keys


def test(ay: Appify, test_task: TestTask) -> (bool, dict):
    ret_data = defaultdict()

    if test_task is None:
        ret_data['msg'] = 'test failed: task is None'
        return False, ret_data
    if test_task.status >= TaskStatus.RUNNING.value:
        ret_data['msg'] = 'build failed: task.status = %d' % test_task.status
        return False, ret_data

    test_task.status = TaskStatus.RUNNING.value
    test_task.is_active = True
    test_task.save()

    ctx = defaultdict()
    ctx[field_keys.TEST_NAME] = test_task.name
    ctx[field_keys.SERVICE_APPIFY] = ay

    account = os.getenv('ENV_MAIL_ACCOUNT')
    pwd = os.getenv('ENV_MAIL_PW')
    ctx[field_keys.SERVICE_MAIL] = mail.Mail(
        account,
        pwd,
    )
    try:
        ctx[field_keys.TEST_INFO] = json.loads(test_task.test_info)
    except JSONDecodeError as e:
        ctx[field_keys.TEST_INFO] = test_task.test_info
    fingerprint = str(int(datetime.now().timestamp()))
    ctx[field_keys.TEST_FINGERPRINT] = fingerprint

    with TestEngine(test_task.name, fingerprint) as engine:
        ret, data = engine.test(ctx)
        ret_data.update(data)

    return ret, ret_data
