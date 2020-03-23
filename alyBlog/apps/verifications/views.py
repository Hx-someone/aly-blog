import logging
import json
import random

from django.views import View
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection

from users import models
from verifications import contains
from utils.captcha.captcha import captcha
from verifications.forms import SmsCodeForm
from utils.yuntongxun.sms import CCP
from utils.res_code.json_function import to_json_data
from utils.res_code.res_code import Code, error_map

logger = logging.getLogger("django")


class ImageCodesView(View):
    """
    image_code view
    """
    def get(self, request, image_code_id):  # 从前端获取到传过来的参数uuid
        verify_text, verify_image = captcha.generate_captcha()  # 生成验证码文本和图片

        # 链接redis步骤 将生成的验证码文本和图片保存到redis中

        # 1.链接redis区
        redis_obj = get_redis_connection(alias="verify_code")

        # 2. 构造键值对
        verify_key = "image_{}".format(image_code_id)

        # 3. 保存数据并设置有效期
        redis_obj.setex(verify_key, contains.IMAGE_CODE_EXPIRE_TIME, verify_text.upper())  # 将所有的验证码保存为大写的

        logger.info('verify_text:{}'.format(verify_text))  # 后台显示验证码信息

        return HttpResponse(content=verify_image, content_type='image/jpg')   # 把验证码和图片返回到前端


class CheckUsernameView(View):
    """
    create username verify view

    # 1. 创建一个类
    request: GET
    params: username
    """
    # 2. 创建个get方法来处理逻辑
    def get(self, request, username):

        # 3. 从数据库中查看是否存在该用户
        data = {
            "username": username,
            "count": models.Users.objects.filter(username=username).count()  # 获取数据库中有几条这个信息:无则0
        }

        # 4. 返回到前端
        return JsonResponse({"data": data})


class CheckMobileView(View):
    """
    create mobile verify view

    # 1.创建一个类
    request: GET
    params: mobile
    """
    # 2. 创建个get方法来处理逻辑
    def get(self, request, mobile):
        # 3. 从数据库中查看是否存在该用户
        data = {
            "mobile": mobile,
            "count": models.Users.objects.filter(mobile=mobile).count()
        }
        # 5. 返回到前端

        return JsonResponse({"data": data})


class SmsCodeView(View):
    """
    # 1. 创建一个SmsCodeView类
    param: mobile、image_text、image_code_id
    """
    # 2. 创建一个post方法用来处理逻辑
    def post(self, request):
        # 3. 获取前端传来的数据
        json_data = request.body

        # 4. 将数据转化为字典
        dict_data = json.loads(json_data)

        # 5. 将数据传递给SmsCodeForm表单进行校验
        form = SmsCodeForm(data=dict_data)

        # 6. 校验成功处理方式
        if form.is_valid():
            # 7. 获取校验后的数据
            mobile = form.cleaned_data.get("mobile")

            # 8. 生成短信验证码
            sms_text = "%06d" % random.randint(0, 999999)

            # 9. 将短信验证码和和过期时间保存到redis中
            redis_obj = get_redis_connection("verify_code")
            sms_text_key = "sms_code_{}".format(mobile).encode("utf8")
            sms_repeat_key = "sms_sixty_{}".format(mobile).encode("utf8")

            redis_obj.setex(sms_text_key, contains.SMS_CODE_EXPIRE_TIME, sms_text)  # key, expire_time, value
            redis_obj.setex(sms_repeat_key, contains.SMS_CODE_EXPIRE_TIME, contains.SMS_REPEAT_EXPIRE_TIME)

            logger.info("发送短信正常[mobile:%s sms_num:%s]" % (mobile, sms_text))  # 调试代码时候用，在控制台显示
            print(sms_text)
            return to_json_data(errmsg="短信发送成功")  # 短信调试

            # # 9. 使用用通讯插件发送短信
            # try:
            #     result = CCP().send_Template_sms(mobile, [sms_text, contains.SMS_CCP_EXPIRE_TIME], contains.SMS_TEMPLATE)
            # except Exception as e:
            #     logger.error("短信发送异常[mobile:{},error:{}]".format(mobile, e))
            #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])  # 短信发送异常
            # else:
            #     if result == 0:  # 发送成功
            #         logger.info("短信发送成功[mobile:{},sms_code:{}]".format(mobile, sms_text))
            #         return to_json_data(errmsg="短信发送正常")
            #     else:  # 发送失败
            #         logger.warning("短信发送失败[mobile:{}]".format(mobile))
            #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])

        # 校验未通过
        else:
            err_msg_list = []

            for item in form.errors.values():
                err_msg_list.append(item[0])

            err_info = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_info)







