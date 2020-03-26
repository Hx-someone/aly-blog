from django.db import models
from utils.models import models as _models
from utils.get_os.get_os import GetOSInfo


class Tags(_models.BaseModel):
    """
    news tags model
    field:
        name            CharField
    """
    name = models.CharField(max_length=64, verbose_name="文章标题", help_text="文章标题")

    class Meta:
        ordering = ["-update_time", "-id"]  # 排序方式
        db_table = "tb_tags"
        verbose_name = "文章标签"  # 在admins站点中的名字
        verbose_name_plural = verbose_name  # 显示复数的名字

    def __str__(self):
        return "文章标签：{}".format(self.name)


class Articles(_models.BaseModel):
    """
    create news model
    field:
        title           CharField
        digest          CharField
        clicks          CharField
        content         TextField
        image_url       URLField

        tag             ForeignKey
        author          ForeignKey
    """
    # CASCADE       :主表删除，从表全部删除
    # PROTECT       :
    # SET_NULL      :主表删除后，从表设置为NULL
    # SET_DEFAULT   :主表删除后，从表设置为默认值
    # SET           :主表删除后，从表调用一个可执行对象，然后将值返回给从表
    # DO_NOTHING    :主表删除后，从表什么都不做

    title = models.CharField(max_length=150, verbose_name="文章标题", help_text="文章标题")
    digest = models.CharField(max_length=200, verbose_name="文章摘要", help_text="文章摘要")
    content = models.TextField(verbose_name="内容", help_text="内容")
    clicks = models.PositiveIntegerField(default=0, verbose_name="文章点击量", help_text="文章点击量")
    image_url = models.URLField(default=" ", verbose_name="图片url", help_text="图片url")
    comment_num = models.PositiveIntegerField(default=0, verbose_name="评论数", help_text="评论数")
    tag = models.ForeignKey("Tags", on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey("users.Users", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-update_time", "-id"]
        db_table = "tb_article"
        verbose_name = "文章"
        verbose_name_plural = verbose_name

    def add_view(self):
        """阅读量+1"""
        self.clicks += 1
        self.save(update_fields=["clicks"])

    def add_comment_num(self):
        """评论数+1"""
        self.comment_num += 1
        self.save(update_fields=["comment_num"])

    def __str__(self):
        return "文章标题：{}".format(self.title)


class HotArticle(_models.BaseModel):
    """
    create hot news model
    field:
        priority        IntegerField
        news         ForeignKey
    """
    PRI_CHOICES = [
        (1, "第一级"),
        (2, "第二级"),
        (3, "第三级"),
    ]

    priority = models.IntegerField(default=3, choices=PRI_CHOICES, verbose_name="优先级", help_text="优先级")

    article = models.OneToOneField("Articles", on_delete=models.CASCADE)

    class Meta:
        ordering = ["-update_time", "-id"]
        db_table = "tb_hotarticle"
        verbose_name = "热门文章"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "优先级：{}".format(self.priority)


class Banner(_models.BaseModel):
    """
    create news banner model
    field:
        priority        IntegerField
        image_url       URLField
        news         ForeignKey
    """
    PRI_CHOICES = [
        (1, "第一级"),
        (2, "第二级"),
        (3, "第三级"),
        (4, "第四级"),
        (5, "第五级"),
        (6, "第六级"),
    ]
    image_url = models.URLField(default="", verbose_name="轮播图url", help_text="轮播图url")
    priority = models.IntegerField(default=6, choices=PRI_CHOICES, verbose_name="优先级", help_text="优先级")

    article = models.OneToOneField("Articles", on_delete=models.CASCADE)

    class Meta:
        ordering = ["priority", "-update_time", "-id"]
        db_table = "tb_banner"
        verbose_name = "轮播图"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "优先级：{}".format(self.priority)


class Comments(_models.BaseModel):
    """
    create news comments models
    field:
        content
        author
        news
        parent
    """
    content = models.TextField(verbose_name="评论内容", help_text="评论内容")
    author = models.ForeignKey("users.Users", on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey("Articles", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)  # 自我关联，多级评论，blank允许前端不传数据

    class Meta:
        ordering = ["-update_time", "-id"]
        db_table = "tb_comments"
        verbose_name = "评论内容"
        verbose_name_plural = verbose_name

    # 自定义字典转化
    def to_dict_data(self):
        print("评论数量：", self.article.comment_num)
        comment_dict_data = {
            "comment_id": self.id,  # 评论id
            "article_id": self.article.id,  # 文章id
            "content": self.content,  # 评论内容
            "update_time": self.update_time.strftime("%Y年%m月%d日"),  # 更新日期
            "author": self.author.username,  # 评论人
            "parent": self.parent.to_dict_data() if self.parent else None  # 二级评论
        }

        return comment_dict_data

    def __str__(self):
        return "评论内容：{}".format(self.content)


class UserLoginInfo(_models.BaseModel):
    """
    create user login log
    field:
        username
        username_type
        ip
        ip_address
        supplier
        user_agent
        last_login_time
    """
    username = models.CharField(max_length=18, verbose_name="用户", help_text="用户")
    user_type = models.CharField(max_length=32, verbose_name="用户类型", help_text="用户类型")
    ip = models.GenericIPAddressField(max_length=15, verbose_name="IP", help_text="IP")
    ip_address = models.CharField(max_length=32, verbose_name="IP地址", help_text="IP地址")
    # supplier = models.CharField(max_length=32, verbose_name="运营商", help_text="运营商")
    user_agent = models.CharField(max_length=128, verbose_name="User-Agent", help_text="User-Agent")
    last_login_time = models.DateTimeField(auto_now=False, auto_now_add=False, verbose_name="登录时间", help_text="登录时间")

    class Meta:
        ordering = ["-update_time", "-id"]
        db_table = "tb_user_login_info"
        verbose_name = "用户登录信息"
        verbose_name_plural = verbose_name

    def get_os_info(self):
        """获取用户信息中浏览器和操作系统信息"""
        info_obj = GetOSInfo(self.user_agent)
        os_name = info_obj.get_os()["family"]
        browser_name = info_obj.get_browser()["family"]
        info = {
            "os_name": os_name,
            "browser_name": browser_name,

        }
        return info

    def __str__(self):
        return "用户登录信息：{}:{}".format(self.username, self.ip_address)
