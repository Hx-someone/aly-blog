from django.db import models

from django.contrib.auth.models import AbstractUser, UserManager as _UserManager


class UserManager(_UserManager):
    """
     重写创建超级用户时需要输入email字段
    """
    def create_superuser(self, username, password, email=None, **extra_fields):
        return super().create_superuser(username=username, password=password, email=email, **extra_fields)


class Users(AbstractUser):
    """
    重写users模型
    """
    objects = UserManager()
    mobile = models.CharField(
        max_length=11,
        unique=True,
        help_text="手机号",
        verbose_name="手机号",
        error_messages={
            "unique": "手机号已被注册"
        })
    email_active = models.BooleanField(default=False, help_text="邮箱状态")


    class Meta:
        db_table = "tb_users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def get_groups_name(self):
        """
        获取到用户组的名字
        :return:
        """
        groups_name_ls = [group.name for group in self.groups.all()]
        return "|".join(groups_name_ls)

    def __str__(self):
        return self.username
