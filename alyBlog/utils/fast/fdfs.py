# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/14 14:39
@Author  : 半纸梁
@File    : fdfs.py
"""
from fdfs_client.client import Fdfs_client  # 上传文件的几个方法从源码中观看

client = Fdfs_client('utils/fast/client.conf')  # 上传配置文件
# 1. 文件名字 client.upload_by_filename
# 2. 文件数据(二进制bytes类型) client.upload_by_buffer
