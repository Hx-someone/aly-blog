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
from itsdangerous import SignatureExpired, TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings

# 滑动验证码
from geetest import GeetestLib
from utils.user_config import user_config
from utils.userinfo_encrypt.decrypt import DeAesCrypt

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

    def get(self, request, token):
        serializer_obj = Serializer(settings.SECRET_KEY, 3600)

        try:
            username = serializer_obj.loads(token)
        except SignatureExpired:
            return HttpResponse("链接已过期")

        username = username.decode()

        user = models.Users.objects.only("is_active").filter(username=username).first()
        user.is_active = True
        user.save(update_fields=["is_active"])

        return render(request, 'users/login.html')


def test(request):
    return render(request, 'users/encrypt.html')




def show_slide_index(request):
    """登录页面显示"""
    return render(request, "users/slide_login.html")

class SlideInitView(View):
    def get(self, reqeust, t):
        """初始化，获取到流水表示并设置状态码"""
        user_id = 'test'
        gt = GeetestLib(user_config.GEETEST_ID, user_config.GEETEST_KEY)
        status = gt.pre_process(user_id)
        if not status:
            status = 2
        reqeust.session[gt.GT_STATUS_SESSION_KEY] = status
        reqeust.session["user_id"] = user_id
        response_str = gt.get_response_str()
        return HttpResponse(response_str)





class SlideLoginView(View):
    def post(self, request):
        gt = GeetestLib(user_config.GEETEST_ID, user_config.GEETEST_KEY)

        # 获取前端传来的登录信息
        en_username = request.POST.get("username")  # 加密的登录账号
        en_password = request.POST.get("password")  # 加密的登录账号
        secret_key = request.POST.get("k")  # 加密的登录账号
        remember = request.POST.get("remember")  # 加密的登录账号

        # 前端传来的geetest的参数
        challenge = request.POST.get(gt.FN_CHALLENGE, "")
        validate = request.POST.get(gt.FN_VALIDATE, "")
        seccode = request.POST.get(gt.FN_SECCODE, "")
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        # 判断滑动验证码是否登录成功
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        # 滑动验证码校验成功后校验用户登录信息
        if result:

            # 解密用户名和登录密码
            decrypt = DeAesCrypt(secret_key, "Pkcs7")
            de_username = decrypt.decrypt_aes(en_username)
            de_password = decrypt.decrypt_aes(en_password)
            login_info = {
                "username": de_username,
                "password": de_password,
                "remember": remember,

            }
            form = LoginForm(login_info, request=request)
            if form.is_valid():

                return to_json_data(errno=Code.OK, errmsg="登录成功")


            else:
                err_msg_list = []
                for item in form.errors.values():
                    err_msg_list.append(item[0])
                err_str = "/".join(err_msg_list)

                return to_json_data(errno=Code.PARAMERR, errmsg=err_str)
        else:
            return to_json_data(errno=Code.LOGINERR, errmsg="验证校验失败")
