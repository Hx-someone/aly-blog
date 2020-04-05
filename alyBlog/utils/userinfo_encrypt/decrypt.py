# -*- coding: utf-8 -*-
"""
@Time    : 2020/4/2 9:32
@Author  : 半纸梁
@File    : decrypt.py
"""
import base64
import hashlib
from Crypto.Cipher import AES, DES


class DeAesCrypt:
    """
    AES-128-CBC解密
    """

    def __init__(self,  key, pad):
        """
        :param data: 加密后的字符串
        :param key: 随机的16位字符
        :param pad: 填充方式
        """
        self.key = key
        self.pad = pad.lower()

        hash_obj = hashlib.md5()  # 构造md5对象
        hash_obj.update(self.key.encode())  # 进行md5加密,md5只能对byte类型进行加密
        res_md5 = hash_obj.hexdigest()  # 获取加密后的字符串数据
        self.iv = res_md5[:16]

    def decrypt_aes(self,data):
        """AES-128-CBC解密"""
        real_data = base64.b64decode(data)
        my_aes = AES.new(self.key, AES.MODE_CBC, self.iv)

        decrypt_data = my_aes.decrypt(real_data)
        return self.get_str(decrypt_data)

    def get_str(self, bd):
        if self.pad == "zero":  # 去掉数据在转化前不足16位长度时添加的ASCII码为0编号的二进制字符
            return ''.join([chr(i) for i in bd if i!=0])
        elif self.pad == "pkcs7":  # 去掉pkcs7模式中添加后面对半的字符
            return ''.join([chr(i) for i in bd if i > 32])
        else:
            return "不存在此种数据填充方式"


class DeDesCrypt:
    """
    DES-128-CBC解密

    """

    def __init__(self, key, pad):
        """
        :param data: 加密后的字符串,在解密是需要先进行base64解密后才行
        :param key: 随机的16位字符
        :param pad: 填充方式
        """
        self.key = key

        self.pad = pad.lower()
        self.iv = base64.b64encode(key.encode())[0:8]

    def decrypt_des(self,data):
        """DES-128-CBC解密"""
        my_des = DES.new(self.key, AES.MODE_CBC, self.iv)
        en_data = base64.b64decode(data.encode())
        decrypt_data = my_des.decrypt(en_data)
        return self.get_str(decrypt_data)

    def get_str(self, bd):
        if self.pad == "zero":  # 去掉数据在转化前不足16位长度时添加的ASCII码为0编号的二进制字符
            return ''.join([chr(i) for i in bd if i!=0])
        elif self.pad == "pkcs7":  # 去掉pkcs7模式中添加后面对半的字符
            return ''.join([chr(i) for i in bd if i > 32])
        else:
            return "不存在此种数据填充方式"


if __name__ == '__main__':
    pkcs7key = "8RfLCXyuhwe9auYE"
    pkcs7iv = "45c84f6bc99ed0fa"
    data = "WISIw8QAHhFtK55rE7oOEtCaqs+7qXXTf60/aTQ380E="
    cl = DeAesCrypt(pkcs7key, "Pkcs7")
    s = cl.decrypt_aes(data)
    print(s)

    des_key = "jxztfZyQ"
    des_iv = "anh6dGZa"
    des_data = "KimY37ACO2I7+POIzzlC8K6+5R7ZJn1J"
    #
    des_obj = DeDesCrypt(des_key,"Zero")
    ds = des_obj.decrypt_des(des_data)
    print(ds)
