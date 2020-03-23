import json
import logging
import markdown
from alyBlog import settings

from django.views import View
from django.shortcuts import render
from haystack.views import SearchView
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from news import contains
from news import models as _models

from utils.res_code.res_code import Code, error_map
from utils.res_code.json_function import to_json_data

logger = logging.getLogger("django")


class IndexView(View):
    """
    create index page
    news_tag

    """

    def get(self, request):
        # 1. 文章标签数据获取
        tag_list = _models.Tags.objects.only("name", "id").filter(is_delete=False)  # 标签数据

        # 2. 热门文章数据获取
        hot_article_list = _models.HotArticle.objects.select_related("article").only("id", "article__title",
                                                                                     "article__image_url").filter(
            is_delete=False).order_by("priority", "-update_time", "-id")
        article_rank = _models.Articles.objects.only("title", "clicks").filter(is_delete=False).order_by("-clicks")[:5]

        return render(request, "news/index.html", locals())


class ArticleView(View):
    def get(self, request):
        # 1. 获取前端传来的数据文章类型id
        try:
            tag_id = int(request.GET.get("tag_id", 0))
        except Exception as e:
            logger.error("文章标签id参数错误：{}".format(e))
            tag_id = 0

        # 2. 获取前端传来的数据页码编号 page_num
        try:
            page_num = int(request.GET.get("page", 1))
        except Exception as e:
            logger.error("文章页码参数错误：{}".format(e))
            page_num = 1

        # 3. 从数据库中获取文章表签id为tag_id的数据
        article_queryset_total = _models.Articles.objects.select_related("author", "tag").only("id", "title", "digest",
                                                                                               "update_time",
                                                                                               "clicks", "image_url",
                                                                                               "author__username",
                                                                                               "tag__name").filter(
            is_delete=False)


        article_tag_queryset = article_queryset_total.filter(is_delete=False, tag_id=tag_id) or \
                               article_queryset_total.filter(is_delete=False)



        # 4. 对数据尽心分页
        pagen = Paginator(article_tag_queryset, contains.PER_PAGE_DATA_NUMBER)  # 传递待分页对象 、每页多少个

        # 5. 返回当页数据
        try:
            article_list = pagen.page(page_num)
        except EmptyPage:
            logger.error("访问页数超过总页数")
            article_list = pagen.page(pagen.num_pages)

        # 6. 数据序列化
        article_per_page_list = []
        for article in article_list:

            article_per_page_list.append({
                "id": article.id,
                "title": article.title,
                "digest": article.digest,
                "update_time": article.update_time.strftime("%Y年%m月%d日"),
                "clicks": article.clicks,
                "image_url": article.image_url,
                "author": article.author.username,
                "comment_num":article.comment_num,
                "tag_name": article.tag.name if article.tag else "",
            })

        data = {
            "total_page": pagen.num_pages,
            "article": article_per_page_list
        }
        return to_json_data(data=data)


class BannerView(View):
    """
    news banner image
    """

    def get(self, request):
        # 1. 从数据库中获取数据
        banner_queryset_list = _models.Banner.objects.select_related("article").only("image_url", "article__id",
                                                                                     "article__title").filter(
            is_delete=False).order_by("priority", "-update_time", "-id")[0:contains.BANNER_IMAGE_NUMBER]

        banner_list = []
        # 2. 数据序列化
        for banner_queryset in banner_queryset_list:
            banner_list.append({
                "image_url": banner_queryset.image_url,
                "article_id": banner_queryset.article.id,
                "article_title": banner_queryset.article.title,
            })

        data = {
            "banner_list": banner_list
        }

        # 3. 返回数据到前端
        return to_json_data(data=data)


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
        article.add_view()  # 阅读数增加1

        # 2. 获取文章评论数据
        comment_queryset_list = _models.Comments.objects.select_related("author", "parent").only("content",
                                                                                                 "update_time",
                                                                                                 "author__username",
                                                                                                 "parent__author__username",
                                                                                                 "parent__content",
                                                                                                 "parent__update_time").filter(
            is_delete=False, article_id=article_id)

        # comment_list = []
        # for comment in comment_queryset_list:
        #     comment_list.append(comment.to_dict_data())  # 引用Comments中自定义的字典转换
        #
        # le = len(comment_list)  # 文章评论数

        # 3. 判断是否取到文章数据
        if article:

            return render(request, "news/article_detail.html", locals())
        else:
            return HttpResponseNotFound("<h1>Page Not Found<h1>")

        # 这里可以在models <comments里面协写一个字典来存放数据>


# 这里可以使用LoginRequiredMinxin类来完成user的获取
class ArticleCommentView(View):
    """
    news comment replay view
    route: /news/<int:article_id>/comments
    """

    # 1. 创建1个post，url带有article_id参数
    def post(self, request, article_id):

        # 要先判断是否用户已经登录（必须登录后才能进行评论）
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])

        # 2. 获取前端传来的参数
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg="参数错误，请重新输入")
            dict_data = json.loads(json_data)
        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 3. 获取前端传来的回复内容
        content = dict_data.get("content")

        # 4. 判断content是否为空
        if not content:
            return to_json_data(errno=Code.PARAMERR, errmsg="评论内容为空，请输入！")

        # 5. 获取父评论id
        parent_id = dict_data.get("parent_id")

        try:
            if parent_id:
                parent_id = int(parent_id)
                # 判断文章id和父评论id是否和传来过同时满足
                if not _models.Comments.objects.only("id").filter(is_delete=False, id=parent_id,
                                                                  article_id=article_id).exists():
                    return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.UNKOWNERR])
        except Exception as e:
            logger.error("父评论id异常：{}".format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg="父评论ID参数异常")

        # 添加评论数
        article = _models.Articles.objects.only("id").filter(id=article_id).first()
        article.add_comment_num()

        # 6. 保存到数据库
        article_comment = _models.Comments()  # 获取评论实例
        article_comment.content = content  # 保存评论内容
        article_comment.article_id = article_id  # 保存评论文章id
        article_comment.author = request.user
        article_comment.parent_id = parent_id if parent_id else None  # 判断是否为空

        article_comment.save()  # 保存实例

        return to_json_data(data={
            "data": article_comment.to_dict_data(),
            "count": article.comment_num   # 文章评论数量
        })


class Search(SearchView):
    template = 'news/search.html'

    def create_response(self):
        # 接收前台用户输入的查询值
        # kw='python'
        query = self.request.GET.get('q', '')
        if not query:
            show = True
            host_news = _models.HotArticle.objects.select_related('article').only('article_id', 'article__title',
                                                                                  'article__image_url').filter(
                is_delete=False).order_by('priority')
            paginator = Paginator(host_news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            try:
                page = paginator.page(int(self.request.GET.get('page', 1)))
            # 假如传的不是整数
            except PageNotAnInteger:
                # 默认返回第一页
                page = paginator.page(1)

            except EmptyPage:
                page = paginator.page(paginator.num_pages)
            return render(self.request, self.template, locals())
        else:
            show = False
            return super(Search, self).create_response()


