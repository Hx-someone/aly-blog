# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/4 13:58
@Author  : 半纸梁
@File    : urls.py
"""
from django.urls import path

from course import views

app_name = "course"

urlpatterns = [
    path("index/", views.CourseIndexView.as_view(), name="index"),
    path("<int:course_id>/", views.CourseDetailView.as_view(), name="course_detail"),
]