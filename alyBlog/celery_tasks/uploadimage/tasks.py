# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/23 18:00
@Author  : 半纸梁
@File    : tasks.py
"""

from celery_tasks.main import app
from utils.fast.fdfs import client

from utils.upload_image.bd_upload_image import BdUploadImage


@app.task(name='upload_server_images')
def upload_server_images(data, file_ext_name):
    """
    图片上传到服务器
    :param data: 图片二进制数据
    :param file_ext_name: 图片后缀名
    :return:
    """

    client.upload_by_buffer(data, file_ext_name)


@app.task(name="upload_bos_images")
def upload_bos_images(bos_host, ak, sk, bucket, image_name, data):
    """

    :param bos_host: bos域名
    :param ak: 百度云access_key_id
    :param sk: 百度云secret_access_key
    :param bucket: 百度云总图片存储库名
    :param image_name: 文件名
    :param data: 图片二进制数据
    :return:
    """
    upload_image = BdUploadImage(bos_host, ak, sk)
    res = upload_image.upload(bucket, image_name, data)
    return res
