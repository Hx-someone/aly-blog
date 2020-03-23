from django.db import models
from utils.models.models import BaseModel


class Teacher(BaseModel):
    """
    create teacher model
    field:
        姓名  name        CharField
        职衔  position    CharField
        简介  brief       TextField
        名言  saying      CharField
        头像  avatar      URLField

    """
    name = models.CharField(max_length=20, verbose_name="姓名", help_text="姓名")
    position = models.CharField(max_length=30, verbose_name="职位", help_text="职位")
    brief = models.TextField(verbose_name="简介", help_text="简介")
    saying = models.CharField(max_length=150, verbose_name="个性签名", help_text="个性签名")
    avatar = models.URLField(default="", verbose_name="姓名", help_text="姓名")

    class Meta:
        db_table = "tb_teacher"
        verbose_name = "讲师"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "姓名：{}".format(self.name)


class CourseCategory(BaseModel):
    """
    create course category model
    field:
        课程名     name        CharField
    """

    name = models.CharField(max_length=30, verbose_name="课程分类名", help_text="课程分类名")

    class Meta:
        db_table = "tb_coursecategory"
        verbose_name = "课程分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "课程分类：{}".format(self.name)


class Course(BaseModel):
    """
    create course model
    field:
        名字      name            CharField
        封面url   cover_url       URLField
        链接url   video_url       URLField
        时长      time            FloatField
        简介      brief           TextField
        课程大纲   outline         TextField
        点击量     clicks          IntegerField
        讲师      teacher         ManyToOne
        类型      category        ManyToOne

    """
    name = models.CharField(max_length=150, verbose_name="课程名", help_text="课程名")
    time = models.FloatField(default=0.0, verbose_name="时长", help_text="时长")
    brief = models.TextField(verbose_name="简介", help_text="简介")
    outline = models.TextField(verbose_name="大纲", help_text="大纲")
    clicks = models.IntegerField(default=0, verbose_name="观看量", help_text="观看量")
    cover_url = models.URLField(null=True, blank=True, verbose_name="封面url", help_text="封面url")
    video_url = models.URLField(null=True, blank=True, verbose_name="视频url", help_text="视频url")

    teacher = models.ForeignKey("Teacher", on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey("CourseCategory", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "tb_course"
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "课程：{}".format(self.name)


    """
    #insert into tb_course (name, cover_url, video_url,brief, outline, time,clicks, teacher_id, category_id, 
    create_time, update_time, is_delete) values
('学会用百度', 'http://kc3nrwmns1rqrn2kzu6.exp.bcevod.com/mda-kc3pnpwigg11k10h/mda-kc3pnpwigg11k10h.jpg', 'http://kc3nrwmns1rqrn2kzu6.exp.bcevod.com/mda-kc3pnpwigg11k10h/mda-kc3pnpwigg11k10h.m3u8','你的测试视频简介', '你的视频大纲', 0.15, 3000,1, 2, now(), now(), 0),

('你的测试视频2名称', 'http://kc3nrwmns1rqrn2kzu6.exp.bcevod.com/mda-kc3pnpk7qy2h33bx/mda-kc3pnpk7qy2h33bx.jpg', 'http://kc3nrwmns1rqrn2kzu6.exp.bcevod.com/mda-kc3pnpk7qy2h33bx/mda-kc3pnpk7qy2h33bx.m3u8', '你的测试视频简介2222', '你的视频大纲22222', 0.17,100,1, 1, now(), now(), 0);


     insert into tb_teacher (name, position, brief, avatar, saying,create_time, update_time, is_delete) values
('小珊神', '美学终极讲师', '讲师简介', '/media/c.jpg',"To be No.2", now(), now(), 0);
Query OK, 1 row affected (0.06 sec)

insert into tb_coursecategory (name, create_time, update_time, is_delete) values
('python基础', now(), now(), 0), 
('python高级', now(), now(), 0), 
('python框架', now(), now(), 0);
    """
