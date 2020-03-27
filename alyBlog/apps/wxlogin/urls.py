# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/26 16:09
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path
from wxlogin import views

app_name = "wxlogin"

urlpatterns = [

    path('wxlogin/', views.WxLoginView.as_view(), name="wxlogin"),

]
