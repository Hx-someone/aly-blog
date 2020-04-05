# -*- coding: utf-8 -*-
"""
@Time    : 2020/2/23 20:38
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path, re_path
from users import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    # path("login/", views.LoginView.as_view(), name="login"),
    path("login/", views.EnLoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("resetPwd/", views.ResetPasswordView.as_view(), name="resetPwd"),

    re_path("active/(?P<token>.*)/", views.EmailVerifyView.as_view(), name='active'),


    path('slide/', views.show_slide_index, name="slide"),  # 显示主页
    path('slide/register-slide/<t>/', views.SlideInitView.as_view(), name="init"),  # 初始化
    path('slide/login/', views.SlideLoginView.as_view(), name="slide_login"),

]
