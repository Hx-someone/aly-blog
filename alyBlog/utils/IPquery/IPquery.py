# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/25 10:34
@Author  : 半纸梁
@File    : test.py
"""
import json
import requests


def get_ip_address(ip):
    """
    IPIP  ip查询归属地
    :param ip: 查询的ip
    :return:
    """
    url = '	http://freeapi.ipip.net/{}'.format(ip)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,\
         like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=0.3)

    data = json.loads(response.text)

    ip_address = data[1] + data[2]  # 地址

    supplier = data[-1]  # 运营商

    return ip_address, supplier


def get_ip_sb_address(ip):
    """
    太平洋IP地址归属查询
    :param ip: 查询的ip
    :return:
    """

    url = "http://whois.pconline.com.cn/ipJson.jsp?ip={}&json=true".format(ip)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,\
             like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=0.3)
    data = json.loads(response.text)

    return data["addr"]


def get_ip_bd_address(ak, ip):
    """
    百度地图 IP归属地查询
    :param ak: 百度地图ak
    :param ip: 查询的ip
    :return:
    """
    url = "http://api.map.baidu.com/location/ip?ak={}&ip={}".format(ak, ip)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,\
             like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=0.3)
    response.encoding = "unicode_escape"
    data = json.loads(response.text)

    return data["content"]["address"]


if __name__ == '__main__':
    """测试ip地址查询"""
    ak = "测试ak"
    ip = "183.220.78.207"
    ip_address, supplier = get_ip_address(ip)

    get_ip_sb_address(ip)

    get_ip_bd_address(ak, ip)
