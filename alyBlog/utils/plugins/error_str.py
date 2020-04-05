# -*- coding: utf-8 -*-
"""
@Time    : 2020/4/5 7:41
@Author  : 半纸梁
@File    : error_str.py
"""


def error_message(form):
    """表单校验失败错误信息"""
    err_msg_list = []
    for item in form.errors.values():
        err_msg_list.append(item[0])

    return "/".join(err_msg_list)
