# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/26 16:21
@Author  : 半纸梁
@File    : ip_spider.py
"""
import time
from django.http import Http404

IP_POOL = {}


# 把这个装饰器装到需要装饰的函数上就行
def ip_spider(ip_spider):
    """黑名单ip"""

    def ip_pool(request):
        now_time = time.time()
        if request.META.get("HTTP_X_FORWARDED_FOR"):
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            ip = request.META.get("REMOTE_ADDR")

        if ip not in IP_POOL:
            IP_POOL[ip] = now_time

        history = IP_POOL.get(ip)

        while history and now_time - history[-1] > 1:
            history.pop()

        if (len(history)) < 3:
            history.insert(0, now_time)
            return ip_spider(request)

        else:
            # 将ip添加到黑名单中，添加到session中，时间为5分钟
            request.session["blackname"] = ip
            request.session.set_expiry(300)
            return Http404("DDDDD")

    return ip_pool


def black(fun):
    """
    白名单ip
    将黑名单中的ip进行判断，禁止访问
    """

    def wihte(request):

        if request.META.get("HTTP_X_FORWARDED_FOR"):
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            ip = request.META.get("REMOTE_ADDR")

        black = request.session.get("blackname")

        if ip == black:
            return Http404()
        else:
            return fun(request)

    return wihte
