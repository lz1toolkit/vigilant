from django.urls import path

import wtest.views as views

app_name = 'wtest'
urlpatterns = [
    path('', views.index, name='index'),
    path(r'test/', views.test, name='test'),
]
