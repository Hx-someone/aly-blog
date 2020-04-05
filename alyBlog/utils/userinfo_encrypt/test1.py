# -*- coding: utf-8 -*-
"""
@Time    : 2020/4/1 23:29
@Author  : 半纸梁
@File    : test1.py
"""

from Crypto.Cipher import AES, DES
import base64
from Crypto.Cipher import AES
import  hashlib
import Crypto
s = b'123\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
aa = ''.join([chr(i) for i in s if i !=0])
print(type(aa))

s2 = b"\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10"
for i in s2:
    print(i)


def get_str(bt):
    """去掉数据在转化前不足16位长度时添加的空格"""
    return''.join([chr(i) for i in bt if i != 0 and i!=16])

key = "tviV3oXXUouON3lB"
hashObj = hashlib.md5()  # 构造md5对象
hashObj.update(key.encode())  # 进行md5加密,md5只能对byte类型进行加密

strMd5Res = hashObj.hexdigest()      # 获取加密后的字符串数据
print(strMd5Res)

vi = "19df12fd1125d17e"
en_data  ="2njd91+7fkkfhjRiXsOLOg=="
def cryptoDe(pwd):
    """AES-128-CBC解密"""
    mode = AES.MODE_CBC
    cipher = AES.new('tviV3oXXUouON3lB', mode, '19df12fd1125d17e')
    decrypted = cipher.decrypt(pwd)
    return decrypted



if __name__ == '__main__':
    # pwd = "d9UWKXHPqIXUxY6QCWheoQ=="
    en_data = "2njd91+7fkkfhjRiXsOLOg=="
    pwd = base64.b64decode(en_data)
    # a = pwd.decode('hex')
    # print(a)

    s = cryptoDe(pwd)
    print("解密后为：{}".format(s))



bd = b'1234567890000000\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10\x10'
print(len(bd))

aab = ''.join([chr(i) for i in bd[:-len(bd)//2]])
print(aab)