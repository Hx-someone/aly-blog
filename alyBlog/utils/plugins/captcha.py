# -*- coding: utf-8 -*-
"""
@Time    : 2020/4/4 21:30
@Author  : 半纸梁
@File    : captcha.py
"""
from django import forms
from django_redis import get_redis_connection


class ImageCaptcha:
    """
    图形验证的存储和获取
    uuid:图形验证的uuid
    text:验证码文本
    alias:存储库名
    expire:过期时间
    """

    def __init__(self, uuid, text, alias, expire=None):
        self.uuid = uuid  # 图形验证码uuid
        self.text = text  # 验证码文本
        self.expire = expire  # 过期时间
        try:
            self.conn = get_redis_connection(alias)  # redis中的存储库名
        except Exception as e:
            raise forms.ValidationError("redis数据库连接错误")

    def captcha_cache(self):
        image_key = "image_{}".format(self.uuid)
        # 3. 保存数据并设置有效期
        self.conn.setex(image_key, self.expire, self.text.upper())  # 将所有的验证码保存为大写的

    @property
    def captcha_validate(self):

        image_key = "image_{}".format(self.uuid).encode("utf8")

        redis_byte_image_text = self.conn.get(image_key)

        self.conn.delete(image_key)

        text = redis_byte_image_text.decode("utf8") if redis_byte_image_text else None
        return text


class MobileCaptcha:
    """
    短信验证的存储和获取
    """

    def __init__(self, mobile, text, alias, expire=None, re_expire=None):
        self.mobile = mobile  # 手机号
        self.text = text  # 短信验证码文本
        self.expire = expire  # 过期时间
        self.re_expire = re_expire  # 重复发送验证码时间
        try:
            self.conn = get_redis_connection(alias)  # redis中的存储库名
        except Exception as e:
            raise forms.ValidationError("redis数据库连接错误")

    def captcha_cache(self):
        # 将短信验证码和和过期时间保存到redis中
        sms_text_key = "sms_code_{}".format(self.mobile).encode("utf8")
        sms_repeat_key = "sms_sixty_{}".format(self.mobile).encode("utf8")

        self.conn.setex(sms_text_key, self.expire, self.text)  # key, expire_time, value
        self.conn.setex(sms_repeat_key, self.expire, self.re_expire)

    @property
    def captcha_validate(self):
        sms_key = "sms_code_{}".format(self.mobile).encode("utf8")  # 短信验证码
        sms_repeat_key = "sms_sixty_{}".format(self.mobile).encode("utf8")  # 短信过期
        redis_sms_text = self.conn.get(sms_key)
        redis_sms_repeat_text = self.conn.get(sms_repeat_key)

        # 用完后就删除该键
        self.conn.delete(sms_key)
        self.conn.delete(sms_repeat_key)

        return redis_sms_text, redis_sms_repeat_text
