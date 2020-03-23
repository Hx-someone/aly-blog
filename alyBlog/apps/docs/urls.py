# -*- coding: utf-8 -*-
"""
@Time    : 2020/2/26 9:11
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path
from docs import views

app_name = "docs"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path("<int:doc_id>/", views.DocDownloadView.as_view(), name="doc_download"),
]
