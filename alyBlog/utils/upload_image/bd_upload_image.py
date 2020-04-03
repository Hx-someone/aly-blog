# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/17 17:29
@Author  : 半纸梁
@File    : bd_upload_image.py

"""

from baidubce.services.bos.bos_client import BosClient
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.bce_client_configuration import BceClientConfiguration
from user_config import user_config


class BdUploadImage(object):
    """
    百度云BOS存储图片插件
    """
    def __init__(self, bos_host, access_key_id, secret_access_key):
        self.bos_host = bos_host
        self.config = BceClientConfiguration(credentials=BceCredentials(access_key_id, secret_access_key),
                                             endpoint=bos_host)
        self.client = BosClient(config=self.config)

    def upload(self, bucket, key, data):
        """
        图片存储库名、文件名、图片二进制数据
        :param bucket:图片存储库名
        :param key:文件名
        :param data:图片二进制数据
        :return:
        """
        res = self.client.append_object_from_string(bucket_name=bucket, key=key, data=data)
        return res


if __name__ == '__main__':
    bos_host = 'https://bj.bcebos.com'
    image_name = "测试"
    bucket = "banzhiliang"
    with open("2018.png", "rb") as f:
        data = f.read()
        upload_image = BdUploadImage(bos_host, user_config.access_key_id, user_config.secret_access_key)
        upload_image.upload(bucket, image_name, data)

