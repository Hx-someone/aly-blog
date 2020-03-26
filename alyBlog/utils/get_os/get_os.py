# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/26 11:29
@Author  : 半纸梁
@File    : get_os.py
"""
from user_agents import parse


class GetOSInfo:
    def __init__(self, ua_string):
        self.user_agent = ua_string

    def get_device(self):
        """
        获取访问用户的设备属性
        测试:只能获取到移动端的设备，不能获取到PC端的设备
        """
        user_agent = parse(self.user_agent)
        device_obj = user_agent.device  # 创建一个设备对象
        family = device_obj.family  # 设备名
        brand = device_obj.brand  # 设备商
        model = device_obj.model  # 设备类型
        data = {
            "family": family,
            "brand": brand,
            "model": model,
        }

        return data

    def get_browser(self):
        """获取访问用户的浏览器属性"""
        user_agent = parse(self.user_agent)
        browser_obj = user_agent.browser  # 创建一个浏览器对象
        family = browser_obj.family  # 浏览器类型
        version = browser_obj.version  # 版本号
        version_string = browser_obj.version_string  # 版本号字符串
        data = {
            "family": family,
            "version": version,
            "version_string": version_string,
        }

        return data

    def get_os(self):
        """获取访问用户的操作系统属性"""
        user_agent = parse(self.user_agent)
        os_obj = user_agent.os  # 创建一个操作系统对象
        family = os_obj.family  # 系统名
        version = os_obj.version  # 系统版本号
        version_string = os_obj.version_string  # 系统版本号字符串
        data = {
            "family": family,
            "version": version,
            "version_string": version_string,
        }

        return data


if __name__ == '__main__':
    """测试信息"""
    ua_string = "Mozilla/5.0 (Linux; Android 6.0.1; OPPO A57 Build/MMB29M; wv) AppleWebKit/537.36 \
    (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.\
    13.0.10 (Baidu; P1 6.0.1)"
    info_obj = GetOSInfo(ua_string)
    device_data = info_obj.get_device()
    browser_data = info_obj.get_browser()
    os_data = info_obj.get_os()

    # print(device_data)
    # print(browser_data)
    # print(os_data)
