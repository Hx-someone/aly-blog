# -*- coding: utf-8 -*-
"""
@Time    : 2020/1/6 22:05
@Author  : 半纸梁
@File    : sms.py
"""
# coding=utf-8

from utils.yuntongxun.CCPRestSDK import REST

# import ConfigParser

# 主帐号
accountSid = '8a216da86d624ac4016d7847c1c31384'

# 主帐号Token
accountToken = 'cb0cfa710869412dae47f23a5273b3d2'

# 应用Id
appId = '8a216da86d624ac4016d7847c218138b'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id


class CCP(object):
    '''自己封装的发送短信的辅助类'''
    # 用来保存对象的类属性
    instance = None

    def __new__(cls):
        # 判断CCP类有没有已经创建好的对象
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)

            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj

        return cls.instance

    def send_Template_sms(self, to, datas, temp_id):
        # 初始化REST SDK
        res = None
        try:
            res = self.rest.sendTemplateSMS(to, datas, temp_id)
        except Exception as e:
            print(e)
        if res.get("statusCode") == "000000":
            return 0
        else:
            # 返回-1 表示发送失败
            return -1
        # for k, v in result.items():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.items():
        #             print('%s:%s' % (k, s))
        #     else:
        #         print('%s:%s' % (k, v))
        #
        #         # sendTemplateSMS(手机号码,内容数据,模板Id)


if __name__ == "__main__":
    ccp = CCP()
    # 注意： 测试的短信模板编号为1
    result = None
    while True:
        result = ccp.send_Template_sms('15397600701', ['8888', 5], 1)
        if result == 0:
            print('短信验证码发送成功！')
            break

