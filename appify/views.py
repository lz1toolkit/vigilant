import json
import os
from io import BytesIO
import datetime

from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

import appify.builder.builder as builder
from appify.builder.objects import BuildResult
from appify.models import (
    TaskStatus, BuildTask,
)
from appify.builder import field_keys


# Create your views here.


def index(request):
    return render(request, 'appify/index.html', {})


@api_view(['POST'])
def build(request):
    stream = BytesIO(request.body)
    data = JSONParser().parse(stream)

    build_task = BuildTask.from_data(data)
    build_task.save()
    if not build_task.id:
        return JsonResponse({"code": -1, "msg": 'build task save failed', "data": data})

    new_task = BuildTask.objects.get(id=build_task.id)
    br: BuildResult = builder.build(new_task.name, new_task.fingerprint, json.loads(new_task.build_info))
    if br.result:
        new_task = BuildTask.objects.get(id=build_task.id)
        new_task.status = TaskStatus.SUCCESS.value
        new_task.apk_info = json.dumps(br.apk_info)
        new_task.is_active = True
        new_task.save()
        return JsonResponse({'code': 0, 'msg': 'success', 'data': data})
    else:
        new_task = BuildTask.objects.get(id=build_task.id)
        new_task.status = TaskStatus.FAILURE.value
        new_task.is_active = True
        new_task.save()
        return JsonResponse({'code': -1, 'msg': br.msg, 'data': data})


@api_view(['GET'])
def apk_info(request):
    build_name = request.GET.get('build_name', default='')
    hours = int(request.GET.get('hours', default=1))
    status = int(request.GET.get('status', default=2))
    count = int(request.GET.get('count', default=1))

    if build_name == '':
        return JsonResponse({'code': -1, 'msg': 'build_name must be assigned'})

    if hours < 1:
        hours = 1

    if count < 1:
        count = 1

    end_time = timezone.now()
    begin_time = end_time - datetime.timedelta(hours=hours)

    # https://docs.djangoproject.com/zh-hans/4.1/ref/models/querysets/#id4
    datas = BuildTask.objects.filter(name=build_name, status=status, create_time__gte=begin_time,
                                     # - 表示 --> desc
                                     create_time__lte=end_time).order_by('-create_time')[:count]

    if not datas:
        return JsonResponse({'code': 0, 'msg': 'success', 'data': {}})

    data = datas[0]
    result = json.loads(data.apk_info)

    return JsonResponse({'code': 0, 'msg': 'success', 'data': result})


@api_view(['GET'])
def download(request):
    name = request.GET.get('name')
    address = request.GET.get('path')

    if not os.path.exists(address):
        return JsonResponse({'code': -1, 'msg:': '%s is not exists.' % address})

    f = open(address, 'rb')
    resp = FileResponse(f)
    resp['Content-Type'] = 'application/octet-stream'
    resp['Content-Disposition'] = 'attachment;filename="{}"'.format(
        name)
    return resp
