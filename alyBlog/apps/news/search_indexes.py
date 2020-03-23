# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/2 14:41
@Author  : 半纸梁
@File    : search_indexes.py
"""

# search_indexes.py这个文件名时固定

from haystack import indexes
from news.models import Articles


class ArticlesIndex(indexes.SearchIndex, indexes.Indexable):
    """
    类名是索引的表名+Index构成

    """
    text = indexes.CharField(document=True, use_template=True)  # 允许使用数据模板
    id = indexes.IntegerField(model_attr="id")   # 数据表中的id
    title = indexes.CharField(model_attr="title")   # 数据表中的title
    digest = indexes.CharField(model_attr="digest")     # 数据表中的digest
    content = indexes.CharField(model_attr="content")   # 数据表中的content
    image_url = indexes.CharField(model_attr="image_url")   # 数据表中的image_url

    def get_model(self):
        """
        返回建立索引的模型类
        :return:
        """
        return Articles

    def index_queryset(self, using=None):
        """
        返回建立索引的数据的query集,去掉一部分不满足条件的文章
        :param using:
        :return:
        """
        return self.get_model().objects.filter(is_delete=False,tag_id__in=[1,2,3,4])


# python manage.py --help  查询所有命令
# python manage.py rebuild_index # 手动创建索引
