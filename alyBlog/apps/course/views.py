from django.shortcuts import render
from course import models
from django.http import Http404


from django.views import View


class CourseIndexView(View):
    """
    course index view
    """
    def get(self, request):
        # 获取课程列表中需要的数据：课程标题，讲师姓名，讲师职位
        course_list = models.Course.objects.select_related("teacher").only("name", "teacher__name",
                                                                      "teacher__position").filter(is_delete=False)
        return render(request, 'course/course.html', locals())


class CourseDetailView(View):
    """
    course detail view

    """
    # 1. 从数据库中获取到需要的课程播放信息：课程名字，教师名字，教师头像，教师简介，教师名言，课程简介，课程大纲，视频url,视频封面url

    def get(self, request, course_id):
        course_detail = models.Course.objects.select_related("teacher").only("name", "brief", "outline", "video_url",
                                                                      "cover_url","teacher__name","teacher__brief",
                                                                      "teacher__avatar","teacher__saying").filter(
            is_delete=False, id=course_id).first()

        if course_detail:
            return render(request, 'course/course_detail.html', locals())
        else:
            raise Http404("课程不存在")


#