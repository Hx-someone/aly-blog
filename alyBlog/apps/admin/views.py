import json
import logging
from datetime import datetime
from urllib.parse import urlencode
from collections import OrderedDict  # 转化为字典

from django.contrib.auth.models import Group, Permission
from django.views import View
from django.http import Http404
from django.db.models import Count
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

from news import models
from admin import contains
from docs.models import Docs
from alyBlog.settings import FDFS_URL
from course.models import Course, CourseCategory, Teacher
from users.models import Users
from utils.fast.fdfs import client
from admin.forms import ArticleEditForm, DocEditForm, CourseEditForm
from utils.page.per_page import get_page_data
from utils.res_code.res_code import Code, error_map
from utils.res_code.json_function import to_json_data
from celery_tasks.uploadimage.tasks import upload_server_images

logger = logging.getLogger("django")


# 后台主页展示
class AdminIndexView(LoginRequiredMixin, View):
    """
    admin index page view
    route:/admin/index/
    permissions:login
    """
    raise_exception = True

    def get(self, request):
        return render(request, 'admin/index/index.html')


# 文章标签展示和创建
class ArticleTagsView(PermissionRequiredMixin, View):  # 使用PermissionRequiredMixin做权限验证
    """
    article tags show and add function View
    route:/admin/tags/
    permissions:view_tags,add_tags
    """

    # 设定有哪些权限的可以访问 文章标签查看和添加权限的。在数据库中app应用可以看到view_tags和add_tags
    permission_required = ('news.view_tags', 'news.add_tags')
    raise_exception = True

    # LOGIN_URL = "users:login"  可以直接在settings中指定，这样整个项目中访问都需要登录

    # 查
    def get(self, request):

        tags = models.Tags.objects.values("id", "name").annotate(
            article_counts=Count(
                "articles")).filter(is_delete=False).order_by("-article_counts",
                                                              "-update_time")
        return render(request, "admin/news/tags.html", locals())

    # 增
    def post(self, request):
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        new_tag_name = dict_data["name"]
        if new_tag_name:
            tag_obj_list = models.Tags.objects.only("name").filter()  # 这里不能选择is_delete

            tag_name_list = [tag_obj.name for tag_obj in tag_obj_list]  # 取出所有的标签名放入到列表中

            if new_tag_name not in tag_name_list:
                models.Tags.objects.create(name=new_tag_name)
                return to_json_data(errmsg="新标签已增加！")
            else:
                return to_json_data(errmsg="标签名已存在")

        else:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])


# 文章标签删除和更新功能
class ArticleTagsManageView(PermissionRequiredMixin, View):
    """
    article tags edit and delete function View
    route:/admin/tags/<int:tag_id>/
    """
    # 设定有哪些权限的可以访问 文章标签查看和添加权限的。在数据库中可以看到view_tags和add_tags
    permission_required = ('news.change_tags', 'delete.add_tags')
    raise_exception = True  # 后台没有权限就报错403

    # 改
    def put(self, request, tag_id):

        # 1. 获取参数
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])
        new_tag_name = dict_data.get("name")

        # 2. 从数据库中获取到id=tag_id的tag_name
        tag_obj = models.Tags.objects.only("name").filter(id=tag_id).first()
        # 3. 判断old_tag_name:是否存在、是否和new_tag_name相同
        if tag_obj:
            old_tag_name = tag_obj.name  # 获取到数据库中的标签名
            if new_tag_name and new_tag_name.strip():  # 新标签名不为空和去掉空格后不为空
                if old_tag_name != new_tag_name:  # 新标签名和旧标签名不能一样
                    tag_obj.name = new_tag_name
                    tag_obj.save(update_fields=["name"])  # 只更新标签名字段

                    return to_json_data(errmsg="更新成功")
                else:
                    return to_json_data(errmsg="标签名未修改")
            else:
                return to_json_data(errmsg="文章标签名为空")

    def delete(self, request, tag_id):
        tag = models.Tags.objects.only("id").filter(is_delete=False,
                                                    id=tag_id).first()
        if tag:
            tag.is_delete = True
            tag.save(update_fields=["is_delete"])
            return to_json_data(errmsg="删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])


# 文章展示汇总
class ArticleManageView(PermissionRequiredMixin, View):
    """
    article list manage view
    route:/admin/article/
    group:view_articles
    """
    permission_required = ("news.view_articles",)
    raise_exception = True

    def get(self, request):
        # 1. 从数据库中查取到文章标签数据：下拉列表
        tags_queryset = models.Tags.objects.only("name").filter(is_delete=False)
        # 2. 从数据库中获取到文章数据：数据展示
        article_queryset = models.Articles.objects. \
            only("id", "title", "create_time", "author__username", "tag__name"). \
            filter(is_delete=False)
        # 3. 获取前端传来的数据：判断1个获取一个：start_time、end_time、article_title、article_author、article_tag

        # 3.1 判断起始时间start_time
        try:
            start_time = request.GET.get("start_time", "").strip()
            start_time = datetime.strptime(start_time, "Y%m%d%")
        except Exception as e:
            # logger.info("起始时间格式错误：{}".format(e))
            start_time = ""

        # 3.2 判断结束时间end_time
        try:
            end_time = request.GET.get("end_time", "").strip()
            end_time = datetime.strptime(end_time, "Y%m%d%")
        except Exception as e:
            # logger.info("起始时间格式错误：{}".format(e))
            end_time = ""

        # 3.3 判断起始时间和结束时间输入的三种情况：1.起始时间有、结束无；2.起始时间无、结束时间有；3.起始时间大于结束时间
        # 3.3.1 起始时间有、结束无
        if start_time and not end_time:
            article_queryset = article_queryset.filter(update_time__lte=start_time)

        # 3.3.2 起始时间无、结束时间有
        if end_time and not start_time:
            article_queryset = article_queryset.filter(update_time__gte=end_time)

        # 3.3.3 起始时间大于结束时间
        if start_time and end_time:
            article_queryset = article_queryset.filter(update_time__range=(start_time, end_time))
            if not article_queryset:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 4. 对文章标题进行判断/模糊查询
        title = request.GET.get("title", "").strip()
        if title:
            article_queryset = article_queryset.filter(is_delete=False, title__icontains=title)

        # 5. 对文章作者进行判断模糊查询
        author = request.GET.get("author", "").strip()
        if author:
            article_queryset = article_queryset.filter(is_delete=False, author__username__icontains=author)

        # 6. 对文章标签进行判断
        tag_id = int(request.GET.get("tag_id", 0))
        article_queryset = article_queryset.filter(is_delete=False, tag_id=tag_id) or article_queryset.filter(
            is_delete=False)

        # 5. 进行分页处理
        try:
            page_num = int(request.GET.get("page", 1))
        except Exception as e:

            logger.info("页码格式错误：{}".format(e))
            page_num = 1

        page_obj = Paginator(article_queryset, contains.PER_PAGE_NUMBER)

        try:
            article_info = page_obj.page(page_num)
        except EmptyPage:  # 页码为空
            article_info = page_obj.page(page_obj.num_pages)

        pages_data = get_page_data(page_obj, article_info)

        # 将时间转化为字符串
        start_time = start_time.strftime("%Y%m%d") if start_time else ""
        end_time = end_time.strftime("%Y%m%d") if end_time else ""
        # 6. 将数据传递给前端
        data = {
            'article_info': article_info,
            'tags': tags_queryset,
            'paginator': page_obj,
            'start_time': start_time,
            'end_time': end_time,
            'title': title,
            'author': author,
            'tag_id': tag_id,
            'other_param': urlencode({
                'start_time': start_time,
                'end_time': end_time,
                'title': title,
                'author': author,
                'tag_id': tag_id,

            })
        }
        data.update(pages_data)

        return render(request, 'admin/news/article_manage.html', context=data)


# 文章编辑和发布和删除
class ArticleEditView(PermissionRequiredMixin, View):
    """
    article edit and pub and delete function view
    route:article/edit/<int:article_id>/
    group:view_articles/delete_articles/change_articles
    """
    permission_required = ('news.view_articles', "news.delete_articles", "news.change_articles")
    raise_exception = True

    def get(self, request, article_id):
        """
        article show
        :param request:
        :param article_id:
        :return:
        """
        # 1. 从数据库中获取到该篇文章
        article = models.Articles.objects.filter(is_delete=False, id=article_id).first()
        if article:

            # 2. 获取到数据库汇总的标签
            tags = models.Tags.objects.only("name").filter(is_delete=False)
            return render(request, 'admin/news/article_edit.html', context={"article": article, "tags": tags})
        else:
            return Http404("文章不存在")

    def delete(self, request, article_id):
        """
        article delete
        :param request:
        :param article_id:
        :return:
        """
        # 1. 从数据库中获取到文章对象
        article = models.Articles.objects.only("id").filter(is_delete=False, id=article_id).first()
        if article:
            article.is_delete = True  # 将逻辑删除改为真
            article.save(update_fields=["is_delete"])
            return to_json_data(errmsg="文章删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

    def put(self, request, article_id):
        """
        article change
        use form verify:article_title、article_digest、article_content、article_tag、image_url
        :param request:
        :param article_id:
        :return:
        """
        # 1. 获取从前端传来的数据和从数据库中获取到文章信息
        article = models.Articles.objects.filter(is_delete=False, id=article_id).first()
        if not article:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode())
        except Exception as e:
            logger.info("文章更新数据获取失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 2. 将数据转化为字典传递给ArticleEditForm表单进行验证
        form = ArticleEditForm(dict_data)
        if form.is_valid():

            # 3. 将数据保存进数据库

            article.title = form.cleaned_data.get("title")
            article.image_url = form.cleaned_data.get("image_url")
            article.digest = form.cleaned_data.get("digest")
            article.content = form.cleaned_data.get("content")
            article.tag = form.cleaned_data.get("tag")
            article.save()
            return to_json_data(errmsg="文章更新成功")
        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)


# 上传图片到服务器
class UploadImageServerView(View):
    def post(self, request):

        # 1. 获取到图片
        image_file = request.FILES.get('image_file')
        if not image_file:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 2. 判断图片后缀名是否是图片格式

        image_ext_name = image_file.name.split(".")[-1]  # 获取到图片的后缀名

        if image_ext_name not in contains.IMAGE_EXT_NAME_LS:
            return to_json_data(errno=Code.PARAMERR, errmsg="图片格式不正确")

        # 3. 判断图片大小是否满足要求
        image_size = image_file.size
        if image_size > contains.IMAGE_MAX_SIZE:
            return to_json_data(errno=Code.PARAMERR, errmsg="图片太大了")

        # 4. 上传图片:看upload_by_buffer源码里面的参数和返回值
        try:
            upload_image = client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.info("图片上传失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg="图片上传失败")
        else:
            # 5. 判断图片是否上传成功
            if upload_image.get("Status") != 'Upload successed.':
                logger.info('图片上传失败')
                return to_json_data(errno=Code.PARAMERR, errmsg="图片上传失败")
            else:
                # 6. 拼接image_url
                image_id = upload_image.get("Remote file_id")
                image_url = FDFS_URL + image_id
                return to_json_data(data={"image_url": image_url}, errmsg="图片上传成功！")


# 使用markdown上传图片
@method_decorator(csrf_exempt, name='dispatch')
class MarkdownImageView(View):
    """
    markdown image upload
    route:/admin/markdown/image
    method:post
    """

    def post(self, request):
        image_file = request.FILES.get("editormd-image-file")
        if not image_file:
            logger.info("从前端获取图片失败")
            return JsonResponse({'success': 0, 'message': '从前端获取图片失败'})

        image_ext_name = image_file.name.split('.')[-1]

        if image_ext_name not in contains.IMAGE_EXT_NAME_LS:
            return JsonResponse({'success': 0, 'message': '图片格式不正确'})

        image_size = image_file.size

        if image_size > contains.IMAGE_MAX_SIZE:
            return JsonResponse({'success': 0, 'message': '图片太大了'})

        try:
            # upload_image = client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
            upload_image = upload_server_images.delay(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.info("图片上传异常：{}".format(e))
            return JsonResponse({'success': 0, 'message': '图片上传失败'})

        else:
            if upload_image.get("Status") != 'Upload successed.':
                return JsonResponse({'success': 0, 'message': '图片上传失败'})
            else:
                image_url = FDFS_URL + upload_image.get('Remote file_id')
                return JsonResponse({'success': 1, 'message': '图片上传成功', "url": image_url})


# 文件上传到服务器
class UploadDocServerView(View):
    def post(self, request):
        # 1. 获取到文档文件
        doc_file = request.FILES.get('doc_file')
        if not doc_file:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 2. 判断文档后缀名是否是文档格式

        doc_ext_name = doc_file.name.split(".")[-1]  # 获取到文档的后缀名

        if doc_ext_name not in contains.DOC_EXT_NAME_LS:
            return to_json_data(errno=Code.PARAMERR, errmsg="文档格式不正确")

        # 3. 判断文档大小是否满足要求
        doc_size = doc_file.size
        if doc_size > contains.DOC_MAX_SIZE:
            return to_json_data(errno=Code.PARAMERR, errmsg="文档太大了")

        # 4. 上传文档:看upload_by_buffer源码里面的参数和返回值
        try:
            upload_doc = client.upload_by_buffer(doc_file.read(), file_ext_name=doc_ext_name)
        except Exception as e:
            logger.info("文档上传失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg="文档上传失败")
        else:
            # 5. 判断文档片是否上传成功
            if upload_doc.get("Status") != 'Upload successed.':
                logger.info('文档上传失败')
                return to_json_data(errno=Code.PARAMERR, errmsg="文档上传失败")
            else:
                # 6. 拼接image_url
                doc_id = upload_doc.get("Remote file_id")
                doc_url = FDFS_URL + doc_id
                return to_json_data(data={"doc_url": doc_url}, errmsg="文档上传成功！")


# 热门文章删改查
class HotArticleView(PermissionRequiredMixin, View):
    """
    hot article add/view/delete/edit function view
    route:/admin/hot_article/  :view
    route:/admin/hot_article/<int:article_id>/  :delete and edit
    permissions:view_hotarticle/change_hotarticle/delete_hotarticle
    """
    permission_required = ("news.view_hotarticle", "news.change_hotarticle", "news.delete_hotarticle")
    raise_exception = True

    def get(self, request):
        """
        hot article view
        :param request:
        :return:
        """
        hot_articles = models.HotArticle.objects.only("id", "priority", "article__title",
                                                      "article__tag__name").filter(is_delete=False).order_by("priority")
        return render(request, 'admin/news/hot_article.html', locals())

    def put(self, request, hot_article_id):
        """
        hot article priority change
        :param request:
        :return:
        """
        # 获取亲阿杜那传来的数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg="参数错误")
            dict_data = json.loads(json_data)
        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg="未知错误")

        # 获取到优先级
        try:
            priority = int(dict_data.get("priority"))
            if priority not in [num for num, word in models.HotArticle.PRI_CHOICES]:  # 判断输入的优先级是否在优先级表中
                return to_json_data(errno=Code.UNKOWNERR, errmsg="设置的优先级不在优先级表中")

        except Exception as e:
            logger.info("热门文章优秀级异常：{}".format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg="热门文章优秀级设置错误")

        # 判断文章是否存在
        hot_article = models.HotArticle.objects.only("id").filter(id=hot_article_id).first()
        if not hot_article:
            return to_json_data(errno=Code.PARAMERR, errmsg="该热门文章不存在")

        # 判断优先级是否有修改
        if hot_article.priority == priority:
            return to_json_data(errno=Code.PARAMERR, errmsg="优先级未修改")

        # 保存
        hot_article.priority = priority
        hot_article.save(update_fields=["priority"])
        return to_json_data(errmsg="优先级修改成功")

    def delete(self, request, hot_article_id):
        """
        hot article delete
        :param request:
        :return:
        """
        hot_article = models.HotArticle.objects.only("id").filter(is_delete=False, id=hot_article_id).first()

        if hot_article:
            hot_article.is_delete = True
            hot_article.save()
            return to_json_data(errmsg="热门文章删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="参数错误")


# 热门文章增：需要单独写一个类视图来处理
class HotArticleAddView(PermissionRequiredMixin, View):
    """
    hot article add view
    route:/admin/hot_article/add/
    permissions:view_hotarticle/add_hotarticle
    """
    permission_required = ("news.view_hotarticle", "news.add_hotarticle")

    def get(self, request):
        """
        传递给前端：tag、article、priority
        :param request:
        :return:
        """
        tags = models.Tags.objects.only("id", "name").filter(is_delete=False).order_by("-id", "-update_time")
        # priority_dict = {k: v for k, v in models.HotArticle.PRI_CHOICES}    # 转化为字典
        priority_dict = OrderedDict(models.HotArticle.PRI_CHOICES)

        return render(request, 'admin/news/hot_add.html', context={"tags": tags, "priority_dict": priority_dict})

    def post(self, request):
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(erno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.info("热门文章添加未知错误：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        try:
            article_id = int(dict_data.get("article_id"))
        except Exception as e:
            logger.info("热门文章id错误：{}".format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        if not models.Articles.objects.only("id").filter(is_delete=False, id=article_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg="文章不存在")

        try:
            priority = int(dict_data.get("priority"))
        except Exception as e:
            logger.info("热门文章优先级错误：{}".format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg="热门文章优先级设置错误")

        priority_ls = [index for index, word in models.HotArticle.PRI_CHOICES]

        if priority not in priority_ls:
            return to_json_data(errno=Code.PARAMERR, errmsg="热门文章优先级设置错误")

        # 创建热门文章
        hot_article_tuple = models.HotArticle.objects.get_or_create(article_id=article_id)
        hot_article, is_create = hot_article_tuple
        hot_article.priority = priority
        hot_article.save(update_fields=["priority"])

        return to_json_data(errmsg="热门文章优先级添加成功")


# 文章分类
class ArticleCategoryView(PermissionRequiredMixin, View):
    """
    article category show
    route:/admin/tags/<int:tag_id>/article/
    permissions:view_tags
    """

    permission_required = ("news.view_tags",)
    raise_exception = True

    def get(self, request, tag_id):
        articles = models.Articles.objects.values("id", "title").filter(is_delete=False, tag_id=tag_id)
        if not articles:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        article_ls = [article for article in articles]
        data = {
            "articles": article_ls
        }

        return to_json_data(data=data)


# 文章发布
class ArticlePubView(PermissionRequiredMixin, View):
    """
    article pub
    route:/admin/article/pub/
    permissions:add_articles/view_tags
    """
    permission_required = ("news.add_articles", "news.view_tags")
    raise_exception = True

    def get(self, request):
        """
        article edit page show
        route:/admin/article/pub/
        :param request:
        :return:
        """
        tags = models.Tags.objects.only("name").filter(is_delete=False)
        return render(request, 'admin/news/article_edit.html', context={"tags": tags})

    def post(self, request):
        """
        article pub function
        use form verify:article_title、article_digest、article_content、article_tag、image_url
        route:/admin/article/pub/
        :param request:
        :return:
        """
        # 1. 获取从前端传来的数据和从数据库中获取到文章信息
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode())
        except Exception as e:
            logger.info("文章发布数据获取失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 2. 将数据转化为字典传递给ArticleEditForm表单进行验证
        form = ArticleEditForm(dict_data)
        if form.is_valid():
            article = form.save(commit=False)
            article.author_id = request.user.id
            article.save()
            return to_json_data(errmsg="文章发布成功")
        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)


# 文章轮播图:查和更新和删除
class ArticleBannerView(PermissionRequiredMixin, View):
    """
    article banner image show and add
    route:/admin/article/banner/ :view
    route:/admin/article/banner/<int:banner_id>/   :delete/put
    permissions:view_banner/change_banner/delete_banner
    """
    permission_required = ("news.view_banner", "news.change_banner", "news.delete_banner")
    raise_exception = True

    def get(self, request):
        """
        article banners show
        route:/admin/article/banner/
        :param request:
        :return:
        """
        banners = models.Banner.objects.filter(is_delete=False).order_by("priority")
        priority = models.Banner.PRI_CHOICES
        pri_dict = OrderedDict(priority)
        return render(request, "admin/news/article_banner.html", context={"banners": banners, "pri_dict": pri_dict})

    def delete(self, request, banner_id):
        """
        article banner image del
        route:/admin/article/banner/<int:banner_id>/
        :param request:
        :param banner_id:
        :return:
        """
        banner = models.Banner.objects.only("id").filter(is_delete=False, id=banner_id).first()
        if not banner:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        else:
            banner.is_delete = True
            banner.save(update_fields=["is_delete"])
            return to_json_data(errmsg="文章轮播图删除成功")

    def put(self, request, banner_id):
        """
        article banner image change
        route:/admin/article/banner/<int:banner_id>/
        :param request:
        :param banner_id:
        :return:
        """
        # 1. 从前端获取到数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.info("轮播图获取失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 2. 判断优先级是否在优先级列表内和为空
        priority = int(dict_data.get("priority"))
        if not priority:
            return to_json_data(errno=Code.PARAMERR, errmsg="优先级不能为空")

        if priority not in [index for index, _ in models.Banner.PRI_CHOICES]:
            return to_json_data(errno=Code.PARAMERR, errmsg="优先级必须在优先级表内")

        # 3. 判断轮播图url是否为空

        image_url = dict_data.get("image_url")
        if not image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg="轮播图url不能为空")

        # 3. 从数据库中拿到该轮播图的信息
        banner = models.Banner.objects.only("priority").filter(is_delete=False, id=banner_id).first()
        if not banner:
            return to_json_data(errno=Code.PARAMERR, errmsg="没有该轮播图")
        ban_priority = banner.priority
        ban_image_url = banner.image_url

        # 4. 判断轮播图有没有做修改
        if ban_priority == priority and ban_image_url == image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg="优先级没有修改")

        banner.priority = priority
        banner.image_url = image_url
        banner.save()
        return to_json_data(errmsg="轮播图优先级修改成功")


# 文章轮播图的添加
class ArticleBannerAddView(PermissionRequiredMixin, View):
    """
    article banner image add
    route:/admin/article/banner/add/
    group: view_tags,add_banner
    """

    permission_required = ("news.view_tags", "news.add_banner")
    raise_exception = True

    def get(self, request):
        """
        article banner image add index page
        :param request:
        :return:
        """
        tags = models.Tags.objects.filter(is_delete=False)
        priority = models.Banner.PRI_CHOICES
        priority_dict = OrderedDict(priority)
        return render(request, 'admin/news/banner_add.html', context={"tags": tags, "priority_dict": priority_dict})

    def post(self, request):
        """
        article banner image add
        route:/admin/article/banner/add/
        :param request:
        :return:
        """
        # 1. 从前端获取到数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.info("轮播图获取失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 2. 判断优先级是否在优先级列表内和为空
        try:
            priority = int(dict_data.get("priority"))
        except Exception as e:
            logger.info("优先级错误：{}".format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        if not priority:
            return to_json_data(errno=Code.PARAMERR, errmsg="优先级不能为空")

        if priority not in [index for index, _ in models.Banner.PRI_CHOICES]:
            return to_json_data(errno=Code.PARAMERR, errmsg="优先级必须在优先级表内")

        # 3. 判断轮播图url是否为空
        image_url = dict_data.get("image_url")
        if not image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg="轮播图url不能为空")

        # 4. 创建文章轮播图
        article_id = dict_data.get("article_id")
        banners = models.Banner.objects.get_or_create(is_delete=False, article_id=article_id)
        banner, is_create = banners

        banner.image_url = image_url
        banner.priority = priority
        banner.save(update_fields=["image_url", "priority"])
        return to_json_data(errmsg="轮播图添加成功")


# 文档主页显示
class DocIndexView(PermissionRequiredMixin, View):
    """
    doc show index
    route:/admin/doc/
    permissions:view_docs
    """
    permission_required = ("docs.view_docs",)
    raise_exception = True

    def get(self, request):
        # 1. 从数据库中获取到文档的数据
        docs = Docs.objects.only("id", "title", "create_time", "author__username").filter(is_delete=False)

        # 2. 获取前端传来的数据：判断1个获取一个：start_time、end_time、doc_title、doc_author
        # 判断起始时间start_time
        try:
            start_time = request.GET.get("start_time", "").strip()
            start_time = datetime.strptime(start_time, "Y%m%d%")
        except Exception as e:
            # logger.info("起始时间格式错误：{}".format(e))
            start_time = ""

        # 判断结束时间end_time
        try:
            end_time = request.GET.get("end_time", "").strip()
            end_time = datetime.strptime(end_time, "Y%m%d%")
        except Exception as e:
            # logger.info("起始时间格式错误：{}".format(e))
            end_time = ""

        # 判断起始时间和结束时间输入的三种情况：1.起始时间有、结束无；2.起始时间无、结束时间有；3.起始时间大于结束时间
        # 起始时间有、结束无
        if start_time and not end_time:
            docs = docs.filter(update_time__lte=start_time)

        # 起始时间无、结束时间有
        if end_time and not start_time:
            docs = docs.filter(update_time__gte=end_time)

        # 起始时间大于结束时间
        if start_time and end_time:
            docs = docs.filter(update_time__range=(start_time, end_time))
            if not docs:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 3. 对文章标题进行判断/模糊查询
        title = request.GET.get("title", "").strip()
        if title:
            docs = docs.filter(is_delete=False, title__icontains=title)

        # 4. 对文章作者进行判断模糊查询
        author = request.GET.get("author", "").strip()
        if author:
            docs = docs.filter(is_delete=False, author__username__icontains=author)

        # 5. 进行分页处理
        try:
            page_num = int(request.GET.get("page", 1))
        except Exception as e:

            logger.info("页码格式错误：{}".format(e))
            page_num = 1

        page_obj = Paginator(docs, contains.PER_PAGE_NUMBER)

        try:
            doc_info = page_obj.page(page_num)
        except EmptyPage:  # 页码为空
            doc_info = page_obj.page(page_obj.num_pages)

        pages_data = get_page_data(page_obj, doc_info)

        # 将时间转化为字符串
        start_time = start_time.strftime("%Y%m%d") if start_time else ""
        end_time = end_time.strftime("%Y%m%d") if end_time else ""
        # 6. 将数据传递给前端
        data = {
            'doc_info': doc_info,
            'paginator': page_obj,
            'start_time': start_time,
            'end_time': end_time,
            'title': title,
            'author': author,
            'other_param': urlencode({
                'start_time': start_time,
                'end_time': end_time,
                'title': title,
                'author': author,
            })
        }
        data.update(pages_data)

        return render(request, 'admin/doc/doc_index.html', context=data)


# 文档发布
class DocPubView(PermissionRequiredMixin, View):
    """
    doc view
    route:/admin/doc/pub/
    permissions:add_docs/view_docs
    """
    permission_required = ("docs.add_docs", "docs.view_docs")
    raise_exception = True

    def get(self, request):
        return render(request, 'admin/doc/doc_edit.html')

    def post(self, request):

        # 1. 获取从前端传来的数据和从数据库中获取到文章信息
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.info("文章发布数据获取失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 2. 将数据转化为字典传递给ArticleEditForm表单进行验证
        form = DocEditForm(dict_data)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.author_id = request.user.id
            doc.save()
            return to_json_data(errmsg="文档创建成功")

        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)


# 文档删除和更新
class DocEditView(PermissionRequiredMixin, View):
    """
    doc delete and change
    route:/admin/doc/edit/<int:doc_id>
    permissions:change_docs/delete_docs/view_docs
    """
    permission_required = ("docs.delete_docs", "docs.change_docs", "docs.view_docs")
    raise_exception = True

    def get(self, request, doc_id):
        """
        doc edit field show
        :param request:
        :param doc_id:
        :return:
        """

        doc = Docs.objects.filter(is_delete=False, id=doc_id).first()
        if doc:
            return render(request, 'admin/doc/doc_edit.html', context={"doc": doc})
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="文档不存在")

    def delete(self, request, doc_id):
        """
        doc delete
        :param request:
        :param doc_id:
        :return:
        """
        doc = Docs.objects.filter(is_delete=False, id=doc_id).first()
        if doc:
            doc.is_delete = True
            doc.save(update_fields=["is_delete"])
            return to_json_data(errmsg="文档删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

    def put(self, request, doc_id):
        """
        article banner image change
        route:/admin/article/banner/<int:banner_id>/
        :param request:
        :param banner_id:
        :return:
        """
        # 1. 从前端获取到数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.info("轮播图获取失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 2.从数据库中获取到该文档信息
        doc = Docs.objects.filter(is_delete=False, id=doc_id).first()
        if not doc:
            return to_json_data(errno=Code.PARAMERR, errmsg="文档不存在")

        # 3. 表单校验并保存到数据库
        form = DocEditForm(dict_data)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                setattr(doc, key, value)
            doc.save()
            return to_json_data(errmsg="文档更新成功")
        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)


# 课程视频展示
class CourseIndexView(PermissionRequiredMixin, View):
    """
    course video show page
    route:/admin/course/
    permissions:view_course
    """
    permission_required = ("course.view_course",)
    raise_exception = True

    def get(self, request):
        # 1. 从数据库中获取到文档的数据
        course = Course.objects.select_related("teacher", "category").only("id", "name", "teacher__name",
                                                                           "category__name", "update_time").filter(
            is_delete=False).order_by("-update_time", "-id")

        category = CourseCategory.objects.only("name").filter(is_delete=False)

        # 2. 获取前端传来的数据：判断1个获取一个：start_time、end_time、doc_title、doc_author
        # 判断起始时间start_time
        try:
            start_time = request.GET.get("start_time", "").strip()
            start_time = datetime.strptime(start_time, "Y%m%d%")
        except Exception as e:
            # logger.info("起始时间格式错误：{}".format(e))
            start_time = ""

        # 判断结束时间end_time
        try:
            end_time = request.GET.get("end_time", "").strip()
            end_time = datetime.strptime(end_time, "Y%m%d%")
        except Exception as e:
            # logger.info("起始时间格式错误：{}".format(e))
            end_time = ""

        # 判断起始时间和结束时间输入的三种情况：1.起始时间有、结束无；2.起始时间无、结束时间有；3.起始时间大于结束时间
        # 起始时间有、结束无
        if start_time and not end_time:
            course = course.filter(update_time__lte=start_time)

        # 起始时间无、结束时间有
        if end_time and not start_time:
            course = course.filter(update_time__gte=end_time)

        # 起始时间大于结束时间
        if start_time and end_time:
            course = course.filter(update_time__range=(start_time, end_time))
            if not course:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 3. 对文章标题进行判断/模糊查询
        name = request.GET.get("name", "").strip()
        if name:
            course = course.filter(is_delete=False, name__icontains=name)

        # 4. 对文章作者进行判断模糊查询
        teacher = request.GET.get("teacher_name", "").strip()
        if teacher:
            course = course.filter(is_delete=False, teacher__name__icontains=teacher)

        cate_id = int(request.GET.get("category", "0"))
        if cate_id:
            course = course.filter(is_delete=False, category=cate_id)

        # 5. 进行分页处理
        try:
            page_num = int(request.GET.get("page", 1))
        except Exception as e:

            logger.info("页码格式错误：{}".format(e))
            page_num = 1

        page_obj = Paginator(course, contains.PER_PAGE_NUMBER)

        try:
            course_info = page_obj.page(page_num)
        except EmptyPage:  # 页码为空
            course_info = page_obj.page(page_obj.num_pages)

        pages_data = get_page_data(page_obj, course_info)

        # 将时间转化为字符串
        start_time = start_time.strftime("%Y%m%d") if start_time else ""
        end_time = end_time.strftime("%Y%m%d") if end_time else ""
        # 6. 将数据传递给前端
        data = {
            'course_info': course_info,
            "categories": category,
            'paginator': page_obj,
            'start_time': start_time,
            'end_time': end_time,
            'name': name,
            'teacher': teacher,
            "cate_id": cate_id,
            'other_param': urlencode({
                'start_time': start_time,
                'end_time': end_time,
                'name': name,
                'teacher': teacher,
                "cate_id": cate_id,
            })
        }
        data.update(pages_data)

        return render(request, 'admin/course/course_index.html', context=data)


# 课程删除和更新
class CourseEditView(PermissionRequiredMixin, View):
    """
    course video delete and change page
    route:/admin/course/edit/<int:course_id>
    permissions:view_course/change_course/delete_course
    """
    permission_required = ("course.view_course", "course.change_course", "course.delete_course")
    raise_exception = True

    def get(self, request, course_id):
        teacher = Teacher.objects.only("id", "name").filter(is_delete=False)
        category = CourseCategory.objects.only("id", "name").filter(is_delete=False)
        course = Course.objects.only("name", "brief", "outline", "teacher__name", "category__name", "cover_url",
                                     "video_url").filter(
            is_delete=False, id=course_id).first()
        data = {
            "teachers": teacher,
            "categories": category,
            "course": course,
        }
        return render(request, 'admin/course/course_edit.html', context=data)

    def delete(self, request, course_id):
        course = Course.objects.only("id").filter(is_delete=False, id=course_id).first()
        if course:
            course.is_delete = True
            course.save(update_fields=["is_delete"])
            return to_json_data(errmsg="删除课程成功！")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="参数错误")

    def put(self, request, course_id):

        # 1. 从前端获取到数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.info("课程更新获取失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 2.从数据库中获取到该课程信息
        course = Course.objects.filter(is_delete=False, id=course_id).first()
        if not course:
            return to_json_data(errno=Code.PARAMERR, errmsg="课程不存在")

        # 3. 表单校验并保存到数据库
        form = CourseEditForm(dict_data)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                setattr(course, key, value)
            course.save()
            return to_json_data(errmsg="课程更新成功")

        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)


# 课程发布
class CoursePubView(PermissionRequiredMixin, View):
    """
    course video add page
    route:/admin/course/pub/
    permissions:view_course/add_course/
    """
    permission_required = ("course.view_course", "course.add_course")
    raise_exception = True

    def get(self, request):
        teacher = Teacher.objects.only("id", "name").filter(is_delete=False)
        category = CourseCategory.objects.only("id", "name").filter(is_delete=False)
        data = {
            "teachers": teacher,
            "categories": category,

        }
        return render(request, 'admin/course/course_edit.html', context=data)

    def post(self, request):
        # 从前端获取到数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.info("课程发布获取失败：{}".format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 表单校验并保存到数据库
        form = CourseEditForm(dict_data)
        if form.is_valid():
            course = form.save(commit=False)
            course.save()
            return to_json_data(errmsg="课程发布成功")
        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)


# 用户组管理展示
class GroupIndexView(PermissionRequiredMixin, View):
    """
    permission group show  page
    route:/admin/group/
    permissions:view_group
    """
    permission_required = ("group.view_group",)
    raise_exception = True

    def get(self, request):
        groups = Group.objects.values("id", "name").annotate(user_num=Count("user")).filter().order_by(
            "user_num")
        data = {
            "groups": groups
        }
        return render(request, "admin/group/group_index.html", context=data)


# 用户组删除和更新
class GroupEditView(PermissionRequiredMixin, View):
    """
   permission group delete and change  page
   route:/admin/group/edit/<int:gro_id>/
   permissions:view_group/change_group/delete_group
   """
    permission_required = ("group.view_group", "group.change_group", "group.delete_group")
    raise_exception = True

    def get(self, request, gro_id):
        group = Group.objects.filter(id=gro_id).first()
        if group:
            permissions = Permission.objects.only("name").all()
            data = {
                "group": group,
                "permissions": permissions
            }
            return render(request, 'admin/group/group_edit.html', context=data)
        else:
            return Http404("Page Not Found ")

    def delete(self, request, gro_id):
        group = Group.objects.filter(id=gro_id).first()
        if group:
            group.permissions.clear()
            group.delete()
            return to_json_data(errmsg="用户组删除成功！")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="删除的用户组不存在")

    def put(self, request, gro_id):

        # 从数据库中获取id=gro_id的组，并判断是否存在
        group = Group.objects.filter(id=gro_id).first()
        if not group:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        # 获取前端传来的数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 判断传来的用户组名是否存在
        group_name = dict_data.get('name', '').strip()  # 用户组名
        if not group_name:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        if group_name != group.name and Group.objects.filter(name=group_name).exists():
            return to_json_data(errno=Code.DATAEXIST, errmsg='组名存在')

        # 校验前端传来的用户组权限
        group_permission = dict_data['group_permission']  # [1,2,3,4,5]
        if not group_permission:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        permission_set = set(index for index in group_permission)

        # 从数据库中获取到该组的权限并判断是否有进行修改
        db_permission_set = set(i.id for i in group.permissions.all())
        if permission_set == db_permission_set:
            return to_json_data(errno=Code.DATAEXIST, errmsg='用户在没有修改')

        # 设置权限，保存进数据库
        for g_id in permission_set:
            per = Permission.objects.get(id=g_id)
            group.permissions.add(per)

        group.name = group_name
        group.save()
        return to_json_data(errmsg='组创建成功')


# 用户组创建
class GroupPubView(PermissionRequiredMixin, View):
    """
      permission group add  page
      route:/admin/group/pub/
      permissions:view_group/add_group
      """
    permission_required = ("group.view_group", "group.add_group")
    raise_exception = True

    def get(self, request):
        permissions = Permission.objects.only("name").all()
        return render(request, 'admin/group/group_edit.html', context={"permissions": permissions})

    def post(self, request):

        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 取出组名，进行判断
        group_name = dict_data.get('name', '').strip()
        if not group_name:
            return to_json_data(errno=Code.PARAMERR, errmsg='组名为空')

        group, is_created = Group.objects.get_or_create(name=group_name)
        if not is_created:
            return to_json_data(errno=Code.DATAEXIST, errmsg='组名已存在')

        # 取出权限进行判断
        group_permissions = dict_data.get('group_permission')
        if not group_permissions:
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数为空')

        try:
            permissions_set = set(int(i) for i in group_permissions)
        except Exception as e:
            logger.info('传的权限参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数异常')

        all_permissions_set = set(i.id for i in Permission.objects.only('id'))
        if not permissions_set.issubset(all_permissions_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的权限参数')

        # 设置权限
        for perm_id in permissions_set:
            p = Permission.objects.get(id=perm_id)
            group.permissions.add(p)

        group.save()
        return to_json_data(errmsg='组创建成功！')


# 用户展示
class UserIndexView(PermissionRequiredMixin, View):
    """
    user show page
    route:/admin/user/
    permissions:view_users
    """
    permission_required = ("users.view_users",)
    raise_exception = True

    def get(self, request):
        users = Users.objects.only("username", "is_staff", "is_superuser", "groups__name").filter(is_active=True)
        return render(request, "admin/user/user_index.html", locals())


# 用户删除和修改
class UserEditView(PermissionRequiredMixin, View):
    """
    user delete and change page
    route:/admin/user/edit/<int:user_id>/
    permissions:view_users/change_users/delete_users
    """
    permission_required = ("users.view_users", "users.change_users", "users.delete_users")
    raise_exception = True

    def get(self, request, user_id):
        user_instance = Users.objects.filter(is_active=True, id=user_id).first()

        if user_instance:
            groups = Group.objects.only("name").all()
            return render(request, "admin/user/user_add.html", locals())
        else:
            return Http404("Update user not exist")

    def delete(self, request, user_id):
        user_instance = Users.objects.only("id").filter(id=user_id).first()
        if user_instance:
            user_instance.groups.clear()  # 去除用户组
            user_instance.user_permissions.clear()  # 去除用户权限
            user_instance.is_active = False
            user_instance.save()
            return to_json_data(errmsg='用户删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="删除的用户不存在")

    def put(self, request, user_id):
        user_instance = Users.objects.filter(id=user_id).first()
        if not user_instance:
            return to_json_data(errno=Code.NODATA, errmsg='该用户不存在')

        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.NODATA])
            dict_data = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 获取到是否是超级管理员、是否有登录后台权限、是否是可用账户，并判断是否在数据库中参数组内
        try:
            is_superuser = int(dict_data['is_superuser'])
            is_staff = int(dict_data.get('is_staff'))
            is_active = int(dict_data['is_active'])

            params = (is_active, is_staff, is_superuser)
            if not all([q in (0, 1) for q in params]):  # 判断参数是否在(0,1)这个元组内
                return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        except Exception as e:
            logger.info('从前端获取得用户参数错误{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        try:
            groups = dict_data.get('groups')
            if groups:
                groups_set = set(int(i) for i in groups)
            else:
                groups_set = set()
        except Exception as e:
            logger.info('用户组参数异常{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='用户组参数异常')

        # 获取到所有的组
        all_groups_set = set(group.id for group in Group.objects.only('id').all())

        # 判断前台传得组是否在所有用户组里面
        if not groups_set.issubset(all_groups_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的用户组参数')

        group_set_all = Group.objects.filter(id__in=groups_set)  # [1,3,4]

        # 保存数据到数据库
        user_instance.groups.clear()
        user_instance.groups.set(group_set_all)
        user_instance.is_staff = bool(is_staff)
        user_instance.is_superuser = bool(is_superuser)
        user_instance.is_active = bool(is_active)
        user_instance.save()
        return to_json_data(errmsg='用户组更新成功')


# 用户访问日志
class LoginLogView(View):
    """
    user login log
    route:/admin/login_log  get
    route:/admin/login_log/edit/<int:info_id>/ delete
    """

    def get(self, request):
        user_login_info = models.UserLoginInfo.objects. \
            only("username", "user_type", "ip", "ip_address", "user_agent", "last_login_time").filter()
        try:
            start_time = request.GET.get("start_time", "").strip()
            start_time = datetime.strptime(start_time, "Y%m%d%")
        except Exception as e:
            start_time = ""

        # 3.2 判断结束时间end_time
        try:
            end_time = request.GET.get("end_time", "").strip()
            end_time = datetime.strptime(end_time, "Y%m%d%")
        except Exception as e:

            end_time = ""

        if start_time and not end_time:
            user_login_info = user_login_info.filter(last_login_time__lte=start_time)

        if end_time and not start_time:
            user_login_info = user_login_info.filter(last_login_time__gte=end_time)

        if start_time and end_time:
            user_login_info = user_login_info.filter(last_login_time__range=(start_time, end_time))
            if not user_login_info:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        username = request.GET.get("username", "").strip()
        if user_login_info:
            user_login_info = user_login_info.filter(is_delete=False, username__icontains=username)

        try:
            page_num = int(request.GET.get("page", 1))
        except Exception as e:

            logger.info("页码格式错误：{}".format(e))
            page_num = 1

        page_obj = Paginator(user_login_info, contains.PER_PAGE_NUMBER)

        try:
            login_info = page_obj.page(page_num)
        except EmptyPage:
            login_info = page_obj.page(page_obj.num_pages)

        pages_data = get_page_data(page_obj, login_info)

        start_time = start_time.strftime("%Y%m%d") if start_time else ""
        end_time = end_time.strftime("%Y%m%d") if end_time else ""

        data = {
            'login_info': login_info,
            'paginator': page_obj,
            'start_time': start_time,
            'end_time': end_time,
            'username': username,
            'other_param': urlencode({
                'start_time': start_time,
                'end_time': end_time,
                'username': username
            })
        }
        data.update(pages_data)

        return render(request, 'admin/login_log/login_log.html', context=data)

    def delete(self, request, info_id):
        info = models.UserLoginInfo.objects.only("id").filter(id=info_id).first()
        if not info:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        info.is_delete = True
        info.save(update_fields=["is_delete"])

        return to_json_data(errmsg="成功删除登录日志信息")
