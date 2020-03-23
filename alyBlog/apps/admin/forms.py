# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/14 19:30
@Author  : 半纸梁
@File    : forms.py
"""
from django import forms
from news.models import Articles, Tags
from docs.models import Docs
from course.models import Course


class ArticleEditForm(forms.ModelForm):
    """
    article pub fields verify
    fields:article_title、article_digest、article_content、article_tag、image_url
    """
    image_url = forms.URLField(label="图片url", error_messages={"required": "图片URL不能为空"})
    tag = forms.ModelChoiceField(queryset=Tags.objects.only("id").filter(is_delete=False), error_messages={
        "required": "文章标签id不能为空"})
    # content = forms.CharField(
    #     label="文章内容",
    #     widget=forms.Textarea(
    #         attrs={"class", "form-group"}
    #     )
    # )

    class Meta:
        model = Articles
        fields = ["title", "digest", "content", "image_url", "tag"]

        error_messages = {
            'title': {
                'max_length': '文章标题长度不能低于150',
                'min_length': '文章标题长度不能低于1',
                'required': '文章标题不能为空'
            },
            'digest': {
                'max_length': '文章摘要长度不能低于200',
                'min_length': '文章摘要长度不能低于1',
                'required': '文章摘要不能为空'
            },
            'content': {
                'required': '文本内容不能为空'
            },
        }


class DocEditForm(forms.ModelForm):
    """
        doc pub fields verify
        fields:doc_title、doc_digest、doc_file_url、doc_image_url
        """
    image_url = forms.URLField(label="图片url", error_messages={"required": "图片URL不能为空"})
    file_url = forms.URLField(label="文件url", error_messages={"required": "文件URL不能为空"})

    class Meta:
        model = Docs
        fields = ["title", "digest", "file_url", "image_url", ]

        error_messages = {
            'title': {
                'max_length': '文档标题长度不能低于150',
                'min_length': '文档标题长度不能低于1',
                'required': '文档标题不能为空'
            },
            'digest': {
                'required': '文档摘要不能为空'
            },
        }


class CourseEditForm(forms.ModelForm):
    """
        course pub fields verify
        fields:doc_title、doc_digest、doc_file_url、doc_image_url
        """
    cover_url = forms.URLField(label="图片url", error_messages={"required": "封面图片URL不能为空"})
    video_url = forms.URLField(label="文件url", error_messages={"required": "视频URL不能为空"})

    class Meta:
        model = Course
        fields = ["name", "brief", "outline", "cover_url", "video_url","teacher","category"]

        error_messages = {
            'name': {
                'max_length': '课程标题长度不能低于150',
                'min_length': '课程标题长度不能低于1',
                'required': '课程标题不能为空'
            },
            'brief': {
                'required': '课程简介不能为空'
            },
            'outline': {
                'required': '课程大纲不能为空'
            },

        }