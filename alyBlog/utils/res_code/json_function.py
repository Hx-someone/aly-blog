# -*- coding: utf-8 -*-
"""
@Time    : 2019/12/22 22:36
@Author  : 半纸梁
@File    : json_function.py
"""
from django.http import JsonResponse

from utils.res_code.res_code import Code


# 处理json格式转化，并加入异常码和异常信息
def to_json_data(errno=Code.OK, errmsg='', data=None, **kwargs):
    """
    返回给前端 json数据以及错误信息
    :param errno: 错误代码
    :param errmsg: 错误信息
    :param data: 数据
    :param kwargs: 不定长数据
    :return:
    """
    json_dict = {'errno': errno, 'errmsg': errmsg, 'data': data}

    if kwargs:
        json_dict.update(kwargs)

    return JsonResponse(json_dict)
