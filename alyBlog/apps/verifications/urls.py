# -*- coding: utf-8 -*-
"""
@Time    : 2020/2/26 21:04
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path, re_path
from verifications import views

app_name = "verifications"

urlpatterns = [
    path("image_code/<uuid:image_code_id>/", views.ImageCodesView.as_view(), name="image_code"),
    re_path("username/(?P<username>\w{5,18})/", views.CheckUsernameView.as_view(), name="username"),
    re_path("mobile/(?P<mobile>1[3-9]\d{9})/", views.CheckMobileView.as_view(), name="mobile"),
    path("sms_code/", views.SmsCodeView.as_view(), name="sms_code"),

    path('index/', views.SlideIndexView.as_view(), name="index"),
    path('index/register-slide/<t>/', views.SlideInitView.as_view(), name="init"),
    path('verify/', views.SlideVerifyView.as_view(), name="verify"),
]
