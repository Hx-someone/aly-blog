# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/6 16:28
@Author  : 半纸梁
@File    : urls.py
"""

from django.urls import path

from admin import views

app_name = "admin"

urlpatterns = [
    path('', views.AdminIndexView.as_view(), name="index"),

    path("tags/", views.ArticleTagsView.as_view(), name="tags"),
    path("tags/<int:tag_id>/", views.ArticleTagsManageView.as_view(), name="tags_manage"),

    path("article/", views.ArticleManageView.as_view(), name="article"),
    path("article/edit/<int:article_id>/", views.ArticleEditView.as_view(), name="article_edit"),
    path("article/pub/", views.ArticlePubView.as_view(), name="article_pub"),

    path("hot_article/", views.HotArticleView.as_view(), name="hot_article"),
    path("hot_article/<int:hot_article_id>/", views.HotArticleView.as_view(), name="hot_article_change"),
    path("hot_add/", views.HotArticleAddView.as_view(), name="hot_add"),
    path("tags/<int:tag_id>/article/", views.ArticleCategoryView.as_view(), name="article_add"),

    path("article/banner/", views.ArticleBannerView.as_view(), name="article_banner"),
    path("article/banner/<int:banner_id>/", views.ArticleBannerView.as_view(), name="banner_edit"),
    path("article/banner/add/", views.ArticleBannerAddView.as_view(), name="banners_add"),

    path("doc/", views.DocIndexView.as_view(), name="doc"),
    path("doc/edit/<int:doc_id>/", views.DocEditView.as_view(), name="doc_edit"),
    path("doc/pub/", views.DocPubView.as_view(), name="doc_pub"),

    path("upload/images/", views.UploadImageServerView.as_view(), name="upload_image"),
    path("markdown/images/", views.MarkdownImageView.as_view(), name="upload_markdown_image"),
    path("upload/doc/", views.UploadDocServerView.as_view(), name="upload_doc"),

    path("course/", views.CourseIndexView.as_view(), name="course"),
    path("course/edit/<int:course_id>/", views.CourseEditView.as_view(), name="course_edit"),
    path("course/pub/", views.CoursePubView.as_view(), name="course_pub"),

    path("group/", views.GroupIndexView.as_view(), name="group"),
    path("group/edit/<int:gro_id>/", views.GroupEditView.as_view(), name="group_edit"),
    path("group/add/", views.GroupPubView.as_view(), name="group_add"),

    path("user/", views.UserIndexView.as_view(), name="user"),
    path("user/edit/<int:user_id>/", views.UserEditView.as_view(), name="user_edit"),

    path("login_log/", views.LoginLogView.as_view(), name='login_log'),
    path("login_log/edit/<int:info_id>/", views.LoginLogView.as_view(), name='login_log_edit'),
]
