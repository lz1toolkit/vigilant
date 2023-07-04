from django.urls import path

import appify.views as views

app_name = 'appify'
urlpatterns = [
    path('', views.index, name='index'),
    path(r'build/', views.build, name='build'),
    path(r'apk', views.apk_info, name='apk_info'),
    path(r'download', views.download, name='download')
]
