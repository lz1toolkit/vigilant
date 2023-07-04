from django.contrib import admin

# Register your models here.

from wtest.models import TestTask


class TestTaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'test_info', 'status', 'create_time',
        'start_time', 'end_time'
    )
    search_fields = ['name', 'create_time']


admin.site.register(TestTask, TestTaskAdmin)
