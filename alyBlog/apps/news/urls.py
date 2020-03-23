# -*- coding: utf-8 -*-
"""
@Time    : 2020/2/26 9:11
@Author  : 半纸梁
@File    : urls.py
"""
from django.urls import path
from news import views


app_name = "news"

urlpatterns = [
    path("index/", views.IndexView.as_view(), name="index"),
    path("article_list/", views.ArticleView.as_view(), name="article_list"),
    path("banner/", views.BannerView.as_view(), name="banner"),
    path("<int:article_id>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("<int:article_id>/comments/", views.ArticleCommentView.as_view(), name="comments"),
    path("search/", views.Search(), name="search"),


]
