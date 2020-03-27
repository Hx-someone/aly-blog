# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/23 21:21
@Author  : 半纸梁
@File    : tasks.py
"""
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from alyBlog import settings
from celery_tasks.main import app
from utils.user_config import user_config


@app.task(name="send_verify_email")
def send_verify_email(username, to_email, rank):
    # send_mail(subject, message, from_email, recipient_list,
    #               fail_silently=False, auth_user=None, auth_password=None,
    #               connection=None, html_message=None):

    auth_user = user_config.EMAIL_HOST_USER
    auth_password = user_config.EMAIL_HOST_PASSWORD

    # 创建一个jws的对象，以SECRET_KEY为加密的参数，过期时间为1h
    serializer_obj = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    user_info = {"username": username}  # 加密的数据dict
    user_info = serializer_obj.dumps(user_info)  # 加密
    token = user_info.decode()  # 转码为字符串

    subject = '新用户激活邮箱验证'
    message = '测试信息'
    from_email = settings.EMAIL_FROM
    recipient_list = [to_email]

    host = settings.SERVER_DOMAIN

    html_message = '<h1>欢迎成为博客的第{}位读者</h1>请点击下面链接激活您的账户:<br/>\
    <a href="{}/users/active/{}">{}/users/active/{}</a>'.format(rank, host, token, host, token)

    send_mail(subject, message, from_email, recipient_list, auth_user=auth_user, auth_password=auth_password,
              html_message=html_message, fail_silently=False)
