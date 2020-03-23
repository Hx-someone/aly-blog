# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/11 16:28
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path

from BDUser import views

app_name = "bd"

urlpatterns = [
    path("register/", views.register, name="register")
]