$(function () {
    let $img = $('.form-item .captcha-graph-img img'); //获取图片信息
    let sImageCodeId='';  //定义一个空字符串用来放uuid字符串
    let $username = $('#user_name');  //获取用户名标签
    let $mobile = $("#mobile"); //获取手机号
    let $smsCodeBtn = $(".form-item .sms-captcha");  //发送短信验证按钮
    let $smsCodeText = $(".form-item .form-captcha");    //图形验证码输入框文本
    let $register = $(".form-contain");       //form表单所有元素  不能获取到submit按钮那里去

    generateImageCode();
    // 当点击验证码时刷新验证码
    $img.click(generateImageCode);


    // 生成图片UUID验证码
    function generateUUID() {
        let d = new Date().getTime();
        if (window.performance && typeof window.performance.now === "function") {
            d += performance.now(); //use high-precision timer if available
        }
        let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            let r = (d + Math.random() * 16) % 16 | 0;
            d = Math.floor(d / 16);
            return (c==='x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
        return uuid;
    }

    //生成验证码图片
    function generateImageCode() {
        sImageCodeId = generateUUID();  //这里不能有let这相当于对前面的sImageCodeId进行修改
        // console.log("第一个uuid:"+sImageCodeId);
        let imageCodeUrl = '/image_code/'+sImageCodeId+"/";  //拼接图片验证码请求路径
        $img.attr('src',imageCodeUrl);  //给图片添加src链接 路径

    }


    //鼠标移出用户名输入框时执行判断
    $username.blur(function () {
        fn_check_username();
    });

    // 用户名是否存在
    function fn_check_username() {
        let sUsername = $username.val(); //获取表单数据
        let sReturnValue = '';
        // 前端校验不
        if (sUsername === ""){
            // alert("用户名不能为空") ;
            // message.showError('用户名能为空！');
            // alert('用户名能为空！');  //这里需要改进
            return
        }else if(!(/\w{5,18}/).test(sUsername)){

            // message.showError('请输入5~18位字符的用户名！');
            // alert('请输入5~18位字符的用户名！');  //这里需要改进
            return
        }

        //ajax请求判断数据库是否存在  后端校验
        $.ajax({
            url:'/username/' + sUsername +'/',
            type:'GET',
            dataType:'json',
            async: false,
            //这里可以使用.done和.fale两个函数俩写返回成功和返回失败
            // success:function(arg) {
            //             //     if(arg.status == true){
            //             //         sReturnValue = 'success'
            //             //     }else{
            //             //         // message.showError('用户名已存在，请重新输入！');
            //             //         alert('用户名已存在，请重新输入！');
            //             //     }
            //             // },
            //             // error:function() {
            //             //     // message.showError('服务器超时，请重试');
            //             //     alert('服务器超时，请重试！');
            //             // }
            success:function (arg) {
                if(arg.data.count !== 0){  // 不等于0表示已经注册了
                    // alert("用户名已注册，请重新输入")
                    sReturnValue = "";
                }else{
                    sReturnValue="success";
                    alert("用户名可以正常使用")
                }
            },
            error:function(){
                alert("用户名ajax,服务器超时，请重新输入");
                sReturnValue = "";
            }
        });

        return sReturnValue  //返回出该信息
    }

    //鼠标移出手机号输入框时执行判断
    $mobile.blur(function() {
        fn_check_mobile();
    });

    // 手机号是否存在
    function fn_check_mobile(){
        let sMobile = $mobile.val();
        let sReturnMobileValue = "";
        // 前端校验
        if (sMobile === ""){
            // alert("手机号输入为空");
            alert("手机号为空");

        }else if(!(/^1[3-9]\d{9}/).test(sMobile)){
            alert("请输入正确的手机号格式") ;

        }
        //ajax请求判断数据库是否存在  后端校验
        $.ajax({
            url:"/mobile/"+sMobile+'/',
            type:"GET",
            dataType: "json",
            async:false,  // 关闭异步
            success:function (arg) {
                if(arg.data.count !== 0){
                    alert(sMobile+"手机号已被注册，请重新输入");
                    sReturnMobileValue = "";
                }else{
                    alert(sMobile+"手机号能正常使用");
                    sReturnMobileValue = "success";
                }
            },
            error:function () {
                alert("手机号ajax,服务器超时，请重新输入");
                sReturnMobileValue = "";
            }
        });
        return sReturnMobileValue  //返回出该信息
    }

    //短信验证
    $smsCodeBtn.click(function(){
        // 判定手机号是否有输入
        if ( fn_check_mobile() !== "success"){
            alert("手机号为空0");
            return
        }
        // 判断用户是否输入图形验证码
        let text = $smsCodeText.val();
        if (!text){
            alert("请输入图形验证码");
            return
        }

        // 判断UUID
        if(!sImageCodeId){
            console.log("第2个"+sImageCodeId);
            alert("图形UUID为空");
            return
        }
        let dataParams={
            'mobile':$mobile.val(),
            'image_text':text,
            "image_code_id":sImageCodeId,
        };
        $.ajax({
            url:"/sms_code/",
            type:"POST",
            data:JSON.stringify(dataParams),
            success:function(arg){
                console.log(arg);
                if(arg.errno==="200"){   // errno: "200", errmsg: "短信发送正常", data: null
                    alert("短信验证码发送成功");
                    //倒计时功能
                    let num = 60;
                    // 设置计时器
                    let t = setInterval(function () {
                        if (num===1){
                            clearInterval(t);
                            $smsCodeBtn.html("重新发送验证码")
                        }else{
                            num -= 1;
                            //展示倒计时信息
                            $smsCodeBtn.html(num+"秒");
                        }

                    },1000)
                }else{
                    alert(arg.errmsg);
                }
            },
            error:function(){
                alert("短信验证ajax,服务器超时，请重试")
            }
        })
    });

    //注册
    $register.submit(function(res){
        //阻止默认提交操作
        res.preventDefault();

        //获取用户输入的内容
        let sUsername = $username.val(); // 用户输入的用户名
        let sPassword = $("input[name=password]").val();  //用户输入的密码
        let sPasswordRepeat = $("input[name=password_repeat]").val(); //用户输入的确认密码
        let sMobile = $mobile.val();   //用户输入的手机号码
        let sSmsCode = $("input[name=sms_captcha]").val();   //短信验证码

        //前端对前面5项进行判定
        //判断用户名是否已被注册
        if (fn_check_username() !=="success"){
            //alert("用户已被注册，请重新输入");
            return
        }
        //判断手机号是否已被注册
        if(fn_check_mobile() !=="success"){
            return
        }
        //判断密码或者确认密码是否为空
        if((!sPassword) || (!sPasswordRepeat)){
            alert("密码或者用户密码不能为空");
            return
        }

        //判断密码和确认密码长度是否合适
        if ((sPassword.length<6 || sPassword.length>20)||(sPasswordRepeat.length<6 || sPasswordRepeat.length>20)){
            alert("密码长度不在6-20范围内");
            return
        }

        //判断密码和确认密码是否一致
        if(sPassword !== sPasswordRepeat){
            alert("两次输入的密码不一致");
            return
        }

        //判断短信验证码输入位数是否为6位
        if(!(/^\d{6}$/).test(sSmsCode)){
            alert("短信验证码长度不正确");
            return
        }

        //发起注册
        //1.注册参数
        let sDataParams ={
            "username": sUsername,
            'mobile': sMobile,
            'password': sPassword,
            'password_repeat': sPasswordRepeat,
            'sms_text': sSmsCode,
        };
        //创建ajax请求
        $.ajax({
            url:"/users/register/",  //请求地址
            type:"POST",            //请求类型
            data:JSON.stringify(sDataParams),  //请求参数
            contentType:"application/json;charset=utf-8", //请求数据类型前端发送给后端的
            dataType:"json",   //后端返回给前端的数据类型
            success:function (arg) {
                if(arg.errno==="200"){
                    alert("恭喜注册成功");
                    //这里需要改进后台管理时
                    setTimeout(function(){
                        window.location.href = "/users/login/";  //注册成功后跳转到登录界面  document.referrer  回到上一个页面
                    },1500);
                }else{
                    alert("注册失败："+arg.errmsg)
                }
            },
            error:function () {
                alert("注册ajax,服务器超时，请重试")
            }
        })

    });


});



