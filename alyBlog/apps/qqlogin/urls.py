# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/26 16:09
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path
from qqlogin import views

app_name = "qqlogin"

urlpatterns = [

    path('qqlogin/', views.QQLoginView.as_view(), name="qqlogin"),

]
