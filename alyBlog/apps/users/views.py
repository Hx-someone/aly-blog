import json
import logging

from django.views import View
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.shortcuts import redirect, reverse

from users import models
from users.forms import RegisterForm, LoginForm, ResetPasswordForm
from utils.res_code.res_code import Code, error_map
from utils.res_code.json_function import to_json_data
from django.http import HttpResponse
from itsdangerous import SignatureExpired,TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings


logger = logging.getLogger("django")



from alyBlog import settings
from celery_tasks.celery_email.tasks import send_verify_email


class RegisterView(View):
    # 1. 创建一个类
    """
    username  用户名
    password   密码
    password_repeat  确认密码
    mobile   电话号码
    sms_text  短信验证码
    """
    # 2. 创建一个get方法，来跳转页面
    def get(self, request):

        return render(request, 'users/register.html')

    # 3. 创建一个post方法来处理逻辑
    def post(self, request):

        # 4. 获取前端传来的数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data)
        except Exception as e:
            # logger.info("注册错误：{}".format(e)) # 调试用
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        # 5. 将数据转化为字典并传入到RegisterForm表单里面
        form = RegisterForm(data=dict_data)

        # 6. RegisterForm验证成功后获取到校验后的的数据
        if form.is_valid():
            username = form.cleaned_data.get("username")
            mobile = form.cleaned_data.get("mobile")
            password = form.cleaned_data.get("password")
            password_repeat = form.cleaned_data.get("password_repeat")

            # 7. 判断密码和确认密码是否一致
            if password != password_repeat:
                return to_json_data(errmsg="密码前后不一致，请重新输入！")

            # 8. 将用户信息保存到数据库
            user = models.Users.objects.create_user(username=username, password=password, mobile=mobile)

            # 9. 跳转到登录页面
            login(request, user)

            # 返回数据到前端
            return to_json_data(errmsg="恭喜您注册成功")

        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)


class LoginView(View):
    """
    # 1. 创建一个LoginView类
    deal login  logic
    param: login_name、password、is_remember_me
    """
    # 2. 创建一个get方法来跳转
    def get(self, request):
        return render(request, "users/login.html")

    # 3. 创建一个post方法来处理主要逻辑
    def post(self, request):

        # 4. 接收前端传来的数据
        try:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])  # 参数错误

            # 5. 将数据转化为字典
            dict_data = json.loads(json_data)

        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])  # 未知错误

        # 6. 将数据和request传递给LoginForm表单进行验证
        form = LoginForm(data=dict_data, request=request)

        # 7. 数据校验成功返回数据给前端
        if form.is_valid():

            return to_json_data(errmsg="恭喜您登录成功")

        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = "/".join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)


class LogoutView(View):
    """
    logout view
    """
    def get(self, request):

        logout(request)
        return redirect(reverse("users:login"))  # 重定向到登录界面


class ResetPasswordView(View):
    """
    修改密码
    """
    def get(self, request):
        return render(request, 'users/reset_password.html')

    def post(self, requests):
        try:
            json_data = requests.body
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data)
        except Exception as e:
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        form = ResetPasswordForm(dict_data)
        if form.is_valid():
            return to_json_data(errmsg="修改密码成功")

        else:
            err_msg_list = []
            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_str)




class EmailVerifyView(View):
    """
    用户邮箱验证
    """
    def get(self,request,token):
        serializer_obj = Serializer(settings.SECRET_KEY,3600)

        try:
            username = serializer_obj.loads(token)
        except SignatureExpired:
            return HttpResponse("链接已过期")

        username = username.decode()

        user = models.Users.objects.only("is_active").filter(username=username).first()
        user.is_active = True
        user.save(update_fields=["is_active"])

        return render(request,'users/login.html')

def test(request):
    username = "hx120841"
    to_email = "1570716789@qq.com"
    send_verify_email.delay(username, to_email, 1)

    return HttpResponse("邮件已发送")