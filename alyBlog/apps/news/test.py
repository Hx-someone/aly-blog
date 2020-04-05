# -*- coding: utf-8 -*-
"""
@Time    : 2020/3/26 0:10
@Author  : 半纸梁
@File    : test.py
"""
a = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'
print(len(a))
username = 1
user_type = 2
ip = 3
ip_address = 4
supplier = 5
user_agent = 6
last_login_name = 7

kwargs = {
    "username": username,
    "user_type": user_type,
    "ip": ip,
    "ip_address": ip_address,

}


def func(username,user_type,ip,ip_address):
    print(username)
    print(user_type)
    print(ip)
    print(ip_address)

func(**kwargs)

from user_agents import parse

u = parse(a)

# Accessing user agent's browser attributes
us = u.browser  # returns Browser(family=u'Mobile Safari', version=(5, 1), version_string='5.1')
c = us.family  # returns 'Mobile Safari'
d = us.version  # returns (5, 1)
e = us.version_string   # returns '5.1'
print(c)
print(d)
print(e)
#
# # Accessing user agent's operating system properties
# user_agent.os  # returns OperatingSystem(family=u'iOS', version=(5, 1), version_string='5.1')
# user_agent.os.family  # returns 'iOS'
# user_agent.os.version  # returns (5, 1)
# user_agent.os.version_string  # returns '5.1'
#
# # Accessing user agent's device properties
# user_agent.device  # returns Device(family=u'iPhone', brand=u'Apple', model=u'iPhone')
# user_agent.device.family  # returns 'iPhone'
# user_agent.device.brand # returns 'Apple'
# user_agent.device.model # returns 'iPhone'
#
# # Viewing a pretty string version
# str(user_agent) # returns "iPhone / iOS 5.1 / Mobile Safari 5.1"
















