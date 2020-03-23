# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/20 12:31
@Author  : 半纸梁
@File    : urls.py
"""
from django.urls import path
from news import views


app_name = "md"

urlpatterns = [
    path("<int:article_id>/", views.ArticleDetailView.as_view(), name="article_detail"),

]
