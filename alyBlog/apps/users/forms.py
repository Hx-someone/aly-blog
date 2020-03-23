# -*- coding: utf-8 -*-
"""
@Time    : 2020/2/27 15:02
@Author  : 半纸梁
@File    : forms.py
"""
import re
from django import forms
from users import models
from django.db.models import Q
from users import contains
from django_redis import get_redis_connection
from django.contrib.auth import login


class RegisterForm(forms.Form):
    """
    register field verify
    """
    # 1. 单字段验证
    username = forms.CharField(
        max_length=18,
        min_length=5,
        error_messages={
            "max_length": "用户名格式不正确",
            "min_length": "用户名格式不正确",
            "required": "用户名不能为空"
        }
    )
    password = forms.CharField(
        max_length=20,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )
    password_repeat = forms.CharField(
        max_length=20,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )

    mobile = forms.CharField(
        max_length=11,
        min_length=11,
        error_messages={
            "max_length": "手机号格式不正确",
            "min_length": "手机号格式不正确",
            "required": "手机号不能为空"
        }
    )
    sms_text = forms.CharField(
        max_length=6,
        min_length=6,
        error_messages={
            "max_length": "短信验证码格式不正确",
            "min_length": "短信验证码格式不正确",
            "required": "短信验证码不能为空"
        }
    )

    # 2. 校验用户名是否已被注册
    def clean_username(self):
        cleaned_username = self.cleaned_data.get("username")
        if models.Users.objects.filter(username=cleaned_username).exists():
            raise forms.ValidationError("用户名已经被注册，请重新输入")
        return cleaned_username

    # 3. 校验手机号是否已被注册
    def clean_mobile(self):
        cleaned_mobile = self.cleaned_data.get("mobile")
        if models.Users.objects.filter(mobile=cleaned_mobile).exists():
            raise forms.ValidationError("手机号已被注册，请重新输入")
        return cleaned_mobile

    # 4. 联合校验获取到清洗后的数据
    def clean(self):
        cleaned_data = super().clean()
        cleaned_password = cleaned_data.get("password")
        cleaned_password_repeat = cleaned_data.get("password_repeat")
        cleaned_mobile = cleaned_data.get("mobile")
        cleaned_sms_code = cleaned_data.get("sms_text")

        # 5. 判断密码和确认密码是一致
        if cleaned_password != cleaned_password_repeat:
            raise forms.ValidationError("密码输入不一致，请重新输入")

        # 6. 判断短信验证码是否和redis中的一致
        redis_obj = get_redis_connection("verify_code")
        sms_key = "sms_code_{}".format(cleaned_mobile).encode("utf8")  # 短信验证码
        sms_repeat_key = "sms_sixty_{}".format(cleaned_mobile).encode("utf8")  # 短信过期
        redis_sms_text = redis_obj.get(sms_key)
        redis_sms_repeat_text = redis_obj.get(sms_repeat_key)

        # 用完后就删除该键
        redis_obj.delete(sms_key)
        redis_obj.delete(sms_repeat_key)

        if not redis_sms_repeat_text:
            raise forms.ValidationError("短信验证码已经过期，请重新获取")

        if (not redis_sms_text) or (cleaned_sms_code != redis_sms_text.decode("utf8")):
            raise forms.ValidationError("短信验证码不正确，请重新输入")


class LoginForm(forms.Form):
    """
    check login field
    param: login_name、password、is_remember_me
    """
    # 1. 校验字段
    login_name = forms.CharField()
    password = forms.CharField(
        max_length=18,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空",
        }
    )
    remember_me = forms.BooleanField(required=False)

    # 2. 重写__init__获取到request数据
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(LoginForm, self).__init__(*args, **kwargs)

    # 3. 单独校验login_name是用户名还是手机号

    def clean_login_name(self):
        login_name = self.cleaned_data.get("login_name")

        # 判断登录名是否为空
        if not login_name:
            raise forms.ValidationError("登录名不能为空")
        # 判断用户名格式满不满足用户名或者手机号格式
        if not (re.match(r'^1[3-9]\d{9}', login_name)) and len(login_name) < 5 or len(login_name) > 18:
            raise forms.ValidationError("登录名格式不正确")

        return login_name

    # 4. 联合校验获取清洗后的数据

    def clean(self):
        cleaned_data = super().clean()
        login_name = cleaned_data.get("login_name")
        password = cleaned_data.get("password")
        remember_me = cleaned_data.get("remember_me")

        user_queryset = models.Users.objects.filter(Q(username=login_name) | Q(mobile=login_name))

        # 5. 从数据库中获取用户信息进行判断
        if user_queryset:
            user = user_queryset.first()

            # 6. 判断密码是否匹配
            if user.check_password(password):

                # 7. 判断是否勾选remember_me
                if remember_me:

                    # 8. 设置session过期时间
                    self.request.session.set_expiry(contains.SESSION_EXPIRE_TIME)  # None是14天
                else:
                    self.request.session.set_expiry(0)

                # 9. 给登录设置session
                login(self.request, user)
            else:
                raise forms.ValidationError("密码不正确，请重新输入")
        else:
            raise forms.ValidationError("用户名不存在，请重新输入")


class ResetPasswordForm(forms.Form):
    login_name = forms.CharField()
    old_password = forms.CharField(
        max_length=20,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )
    new_password = forms.CharField(
        max_length=20,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )
    re_new_password = forms.CharField(
        max_length=20,
        min_length=6,
        error_messages={
            "max_length": "密码格式不正确",
            "min_length": "密码格式不正确",
            "required": "密码不能为空"
        }
    )

    # 单独校验登录名
    def clean_login_name(self):
        login_name = self.cleaned_data.get("login_name")
        if not login_name:
            raise forms.ValidationError("登录名不能为空")

        if not re.match(r"^1[3-9]{9}$]", login_name) and len(login_name) < 5 \
                or len(login_name) > 18:
            raise forms.ValidationError("登录名格式不正确")

        return login_name

    def clean(self):
        cleaned_data = super().clean()
        login_name = cleaned_data.get("login_name")
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        re_new_password = cleaned_data.get("re_new_password")

        user_queryset = models.Users.objects.filter(Q(username=login_name) |
                                                    Q(mobile=login_name))

        if user_queryset:
            user = user_queryset.first()
            if user.check_password(old_password):  # 判断密码是否和登录名对的上
                if new_password == re_new_password:  # 判断新密码输入是否一致
                    if old_password != new_password:  # 判断新密码和旧密码是否一致
                        user.set_password(new_password)  # 更新新密码
                        user.save()
                    else:
                        raise forms.ValidationError("密码未做修改")
                else:
                    raise forms.ValidationError("新密码前后输入不一致，请重新输入")
            else:
                raise forms.ValidationError("密码输入不正确，请重新输入密码")
        else:
            raise forms.ValidationError("用户名不存在，请重新输入")











