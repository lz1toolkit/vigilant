import os
from io import BytesIO

from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from rest_framework.decorators import api_view

from wtest.models import TestTask, TaskStatus
from wtest.tester import tester
from wtest.client import appify


def index(request):
    return render(request, 'wtest/index.html', {})


def go_to_test(data):
    test_task = TestTask.from_data(data)
    test_task.save()

    task_id = test_task.id
    if not task_id:
        return False, 'test task save failed'

    new_task = TestTask.objects.get(id=task_id)
    b, data = tester.test(appify.Appify(os.getenv('APPLIFY_BASE_URL')), new_task)
    if b:
        new_task = TestTask.objects.get(id=task_id)
        new_task.status = TaskStatus.SUCCESS.value
        new_task.is_active = True
        new_task.save()
        return True, 'success'
    else:
        new_task = TestTask.objects.get(id=task_id)
        new_task.status = TaskStatus.FAILURE.value
        new_task.is_active = True
        new_task.save()
        return False, 'failure'


@api_view(['POST'])
def test(request):
    stream = BytesIO(request.body)
    data = JSONParser().parse(stream)

    b, msg = go_to_test(data)
    return JsonResponse({'code': 0 if b else -1, 'msg': msg, 'data': data})
