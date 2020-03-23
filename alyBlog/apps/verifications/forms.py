# -*- coding: utf-8 -*-
"""
@Time    : 2020/2/27 9:49
@Author  : 半纸梁
@File    : forms.py
"""
from django import forms
from django_redis import get_redis_connection
from django.core.validators import RegexValidator


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

        # 2. 建立redis链接
        try:
            redis_obj = get_redis_connection("verify_code")
        except Exception as e:
            raise forms.ValidationError("redis数据库连接错误")

        # 3. 构建image_code查询的键
        image_code_key = "image_{}".format(image_code_uuid).encode("utf8")

        # 4. 获取数据库中的image_code的值
        redis_byte_image_text = redis_obj.get(image_code_key)

        # 5. 删除redis中该uuid的键
        redis_obj.delete(image_code_key)  #

        # 6. 将拿到的值化为utf8字符：redis中拿到的值都是二进制
        redis_image_text = redis_byte_image_text.decode("utf8") if redis_byte_image_text else None

        # 7. 判断现在的image_text和redis_image_text是否一致
        if image_text.upper() != redis_image_text:
            raise forms.ValidationError("图形验证码校验失败")

        # 8. 判断60秒内是否有重复发送短信
        redis_sms_repeat_key = "mobile_{}".format(mobile).encode("utf8")  # 构建短信60秒内发送查询的键
        if redis_obj.get(redis_sms_repeat_key):
            raise forms.ValidationError("短信发送太频繁，请稍后再试")








