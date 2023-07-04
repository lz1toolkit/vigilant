from django.contrib import admin

# Register your models here.

from appify.models import BuildTask


class BuildTaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'fingerprint', 'build_info', 'status', 'apk_info', 'create_time',
        'start_time', 'end_time')
    search_fields = ['name', 'create_time']


admin.site.register(BuildTask, BuildTaskAdmin)
