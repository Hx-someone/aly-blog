# -*- coding: utf-8 -*-
"""
@Time    : 2020/2/27 9:49
@Author  : 半纸梁
@File    : forms.py
"""
from django import forms
from django.core.validators import RegexValidator
from utils.plugins.captcha import ImageCaptcha

mobile_reg = RegexValidator(r"^1[3-9]\d{9}","手机号格式不正确")


class SmsCodeForm(forms.Form):
    """
    check sms_code field
    """
    mobile = forms.CharField(
        max_length=11,
        min_length=11,
        validators=[mobile_reg],
        error_messages={
            "max_length": "手机号格式不正确",
            "min_length": "手机号格式不正确",
            "required": "手机号不能为空"
        }
    )

    image_code_id = forms.UUIDField(error_messages={"required": "UUID不能为空"})
    image_text = forms.CharField(
        max_length=4,
        min_length=4,
        error_messages={
            "max_length": "图形验证码格式不正确",
            "min_length": "图像验证码格式不正确",
            "required": "图形验证码不能为空"
        }
    )

    def clean(self):
        # 1. 获取清洗后的数据
        cleaned_data = super().clean()
        mobile = cleaned_data.get("mobile")
        image_code_uuid = cleaned_data.get("image_code_id")
        image_text = cleaned_data.get("image_text")

        # 图形验证码获取
        # print("前端传来获取的：{}".format(image_code_uuid))
        image_captcha = ImageCaptcha(image_code_uuid, image_text, alias="verify_code")
        redis_image_text = image_captcha.captcha_validate

        if image_text.upper() != redis_image_text:
            raise forms.ValidationError("图形验证码校验失败")

        # 8. 判断60秒内是否有重复发送短信
        redis_sms_repeat_key = "mobile_{}".format(mobile).encode("utf8")  # 构建短信60秒内发送查询的键

        if image_captcha.conn.get(redis_sms_repeat_key):
            raise forms.ValidationError("短信发送太频繁，请稍后再试")








