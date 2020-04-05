$(function () {
    let handler = function (captchaObj) {

        captchaObj.onSuccess(function () {
            let result = captchaObj.getValidate();
            let sUsername = $("input[name=username]").val();//获取用户登录名输入值
            let sPassword = $("input[name=password]").val();  //获取用户密码输入框
            let sRemember = $("input[type=checkbox]").is(":checked"); //获取用户记住密码选择框


            //1.判断用户名是否为空
            if (!sUsername) {
                message.showError("用户名输入为空，请重新输入");
                return
            } else if (!(/\w{5,18}/).test(sUsername)) {
                message.showError("用户名输入格式不正确，请重新输入");
                return
            }
            //2.判断密码是否为空
            if (!sPassword) {
                message.showError("密码输入为空，请重新输入");
                return
            } else if (!(/\w{5,20}/).test(sPassword)) {
                message.showError("密码输入格式不正确，请重新输入");
                return
            }

            //将账号密码加密
            let sKey = randomNum(16);
            let sEnUsername = aesPkcs7Encrypt(sUsername, sKey);
            let sEnPassword = aesPkcs7Encrypt(sPassword, sKey);
            if (!result) {
                message.showError("请先完成验证校验");
                return
            }

            $.ajax({
                url: '/users/slide/login/',
                type: 'POST',
                dataType: 'json',
                data: {
                    username: sEnUsername,  //用户名
                    password: sEnPassword,  //用户密码
                    k: sKey,  //加密的秘钥key
                    remember: sRemember,  //是否记住密码
                    geetest_challenge: result.geetest_challenge,
                    geetest_validate: result.geetest_validate,
                    geetest_seccode: result.geetest_seccode
                },

            })
                .done(function (res) {
                    if (res.errno === "200") {
                        message.showSuccess("执行到此2");
                        setTimeout(function () {
                            window.location.href = '/news/index'
                        }, 800)
                    } else {
                        setTimeout(function () {
                            message.showError('账号或者用户名错误，请重试' + res.errmsg);
                            captchaObj.reset();
                        }, 800);
                    }
                })
                .fail(function () {
                    message.showError("服务器超时，请重试！")
                })
        })

        $("#btn").click(function () {
            captchaObj.show()
        })
        captchaObj.appendTo("#captcha");
    }

//向后端发送请求，获取到配置参数
    $.ajax({
        url: "/users/slide/register-slide/" + (new Date()).getTime() + "/", // 加随机数防止缓存
        type: "get",
        dataType: "json",
        success: function (data) {

            $('#text').hide();
            $('#wait').show();
            // 调用 initGeetest 进行初始化
            // 参数1：配置参数
            // 参数2：回调，回调的第一个参数验证码对象，之后可以使用它调用相应的接口
            initGeetest({
                // 以下 4 个配置参数为必须，不能缺少
                gt: data.gt,
                challenge: data.challenge,
                offline: !data.success, // 表示用户后台检测极验服务器是否宕机
                new_captcha: data.new_captcha, // 用于宕机时表示是新验证码的宕机

                product: "float", // 产品形式，包括：float，popup
                width: "440px",
                https: true
            }, handler);
        }
    })
})

