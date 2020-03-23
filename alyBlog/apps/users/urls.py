# -*- coding: utf-8 -*-
"""
@Time    : 2020/2/23 20:38
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("resetPwd/", views.ResetPasswordView.as_view(), name="resetPwd")
]
