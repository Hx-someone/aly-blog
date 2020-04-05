# -*- coding: utf-8 -*-
"""
@Time    : 2020/4/3 21:29
@Author  : 半纸梁
@File    : distance.py
"""
import math
import json
import requests
from user_config import user_config


def radians(num):
    """将度数转化为弧度"""
    return num * math.pi / 180


def distance(lng1, lat1, lng2, lat2):
    """
    计算两个经纬度之间的直线距离
    经度：-180~180
    纬度：-90~90
    :param lng1: 经度1
    :param lat1: 纬度1
    :param lng2: 经度2
    :param lat2: 纬度2
    :return: 距离，单位：km，保留3位小数
    """
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    lng = lng2 - lng1  # 弧度差
    lat = lat2 - lat1  # 弧度差
    a = math.sin(lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(lng / 2) ** 2
    s = 2 * math.asin(math.sqrt(a))
    r = 6371.371
    return round(s * r, 3)


def city_coordinate(ip):
    """
    将ip地址定位:返回城市左下和右上两个点经纬度
    :param ip: ip地址
    :return: dot_ls 左下，右上经纬度坐标，[(lng1,lat1),(lng2,lat2)]
    """
    url = "https://restapi.amap.com/v3/ip?parameters"
    parameters = {
        "ip": ip,
        "key": user_config.LBS_WEB_KEY
    }

    result = requests.get(url, parameters, timeout=2)
    data = result.text
    dot_ls = [tuple(i.split(",")) for i in json.loads(data)["rectangle"].split(";")]
    return dot_ls


def centre_dot(dot_ls):
    """计算多个经纬度坐标的中心点"""
    lng = 0
    lat = 0
    count = len(dot_ls)
    for dot in dot_ls:
        lng += float(dot[0]) * math.pi / 180
        lat += float(dot[1]) * math.pi / 180

    lng /= count
    lat /= count
    center_dot = (lng * 180 / math.pi, lat * 180 / math.pi)
    return center_dot


def address(coordinate, key, poitype=None, radius=None):
    """显示经纬度规定范围内的建筑信息和街道信息"""
    url = "https://restapi.amap.com/v3/geocode/regeo?parameters"
    parameters = {
        "location": coordinate,  # 经纬度坐标字符串
        "key": key,  # 高德web key
        "radius": radius if radius else 100,  # 范围，默认为100米
        "poitype": poitype,  # 搜索类型
        "extensions": "all"  # 显示结果控制

    }

    result = requests.get(url, parameters)
    return json.loads(result.text)


""""
30.53006918,103.9017713
30.79041003 , 104.2544496
"""
res = address("103.9017713,30.53006918", user_config.LBS_WEB_KEY)
# print(res)

dot_ls = city_coordinate("183.220.74.131")
print(dot_ls)
center_dot = centre_dot(dot_ls)
print(center_dot)
