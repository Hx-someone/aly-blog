from django.db import models
from utils.models.models import BaseModel


class Docs(BaseModel):
    """
    create doc model
    """
    file_url = models.URLField(verbose_name="文件url", help_text="文件url")
    title = models.CharField(max_length=150, verbose_name="文档名", help_text="文档名")
    digest = models.TextField(verbose_name="文档简介", help_text="文档简介")
    image_url = models.URLField(verbose_name="图片url", help_text="图片url")
    author = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_docs"
        verbose_name = "下载文档"
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.title

