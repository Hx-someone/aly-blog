import logging
import markdown

from django.views import View
from django.shortcuts import render
from django.http import HttpResponseNotFound
from news import models as _models

logger = logging.getLogger("django")


class ArticleDetailView(View):
    """
    news detail
    """

    def get(self, request, article_id):
        # 1. 从数据库Articles中获取id=article_id的数据：title、update_time、content、tag_name、author,
        article = _models.Articles.objects.select_related("author", "tag").only("id", "title", "update_time", "content",
                                                                                "tag__name",
                                                                                "author__username").filter(
            is_delete=False, id=article_id).first()

        # 2. 获取文章评论数据
        comment_queryset_list = _models.Comments.objects.select_related("author", "parent").only("content",
                                                                                                 "update_time",
                                                                                                 "author__username",
                                                                                                 "parent__author__username",
                                                                                                 "parent__content",
                                                                                                 "parent__update_time").filter(
            is_delete=False, article_id=article_id)

        comment_list = []
        for comment in comment_queryset_list:
            comment_list.append(comment.to_dict_data())  # 引用Comments中自定义的字典转换

        le = len(comment_list)  # 文章评论数

        # 3. 判断是否取到文章数据
        if article:

            return render(request, "test/test.html", locals())
        else:
            return HttpResponseNotFound("<h1>Page Not Found<h1>")

        # 这里可以在models <comments里面协写一个字典来存放数据>


