import json
import random
import logging

from django.views import View
from django.http import HttpResponse, JsonResponse

from users import models
from verifications import contains
from utils.res_code.res_code import Code
from utils.captcha.captcha import captcha
from verifications.forms import SmsCodeForm
from celery_tasks.sms.tasks import send_sms_code
from utils.plugins.error_str import error_message
from utils.res_code.json_function import to_json_data
from utils.plugins.captcha import ImageCaptcha, MobileCaptcha

logger = logging.getLogger("django")


class ImageCodesView(View):
    """
    image_code view
    """

    def get(self, request, image_code_id):  # 从前端获取到传过来的参数uuid
        verify_text, verify_image = captcha.generate_captcha()  # 生成验证码文本和图片
        print("前端传来存储的：{}".format(image_code_id))

        # 链接redis步骤 将生成的验证码文本和图片保存到redis中
        image_code = ImageCaptcha(image_code_id, verify_text, alias="verify_code",
                                  expire=contains.IMAGE_CODE_EXPIRE_TIME)
        image_code.captcha_cache()

        logger.info('verify_text:{}'.format(verify_text))  # 后台显示验证码信息

        return HttpResponse(content=verify_image, content_type='image/jpg')  # 把验证码和图片返回到前端


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
            #  9. 将短信验证码和和过期时间保存到redis中
            mobile_captcha = MobileCaptcha(mobile, sms_text, alias="verify_code", expire=contains.SMS_CODE_EXPIRE_TIME,
                                           re_expire=contains.SMS_REPEAT_EXPIRE_TIME)
            mobile_captcha.captcha_cache()

            # 使用celery异步处理短信发动任务
            print(sms_text)
            send_sms_code.delay(mobile, sms_text, contains.SMS_CODE_EXPIRE_TIME, contains.SMS_TEMPLATE)
            return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")

        # 校验未通过
        else:
            err_info = error_message(form)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_info)
