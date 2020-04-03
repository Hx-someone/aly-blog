$(function () {
    let $loginName = $("#user"); //获取用户登录名输入框
    let $login = $(".form-contain");  //获取整个登录表单

    //判断鼠标移出用户名时判断是否为空
    $loginName.blur(function () {
        fn_check_user();
    });

    //判断用户是否输入满足条件
    function fn_check_user() {
        let sUsername = $loginName.val(); // 获取用户输入的登录名

        //前端校验
        //1.判断用户名是否为空
        if(sUsername===""){
            message.showError("用户名输入为空，请重新输入");
            return
        }else if(!(/\w{5,18}/).test(sUsername)){
            message.showError("用户名输入格式不正确，请重新输入");
            return
        }
    }

    $login.submit(function (arg) {
        arg.preventDefault();  //阻止form表单默认提交

        //获取参数
        let $userAccount = $("input[name=login_name]").val();//获取用户登录名输入值
        let $pwd = $("input[name=password]").val();  //获取用户密码输入框
        let $remember = $("input[type=checkbox]").is(":checked"); //获取用户记住密码选择框

        //1.判断用户名是否为空
        if($userAccount===""){
            message.showError("用户名输入为空，请重新输入");
            return
        }else if(!(/\w{5,18}/).test($userAccount)){
            message.showError("用户名输入格式不正确，请重新输入");
            return
        }

        //构造ajax请求参数
        let sDataParams = {
            'login_name': $userAccount,  //获取前端输入的登录名
            'password': $pwd,   //获取前端输入的密码
            'remember_me': $remember  //获取前端是否有选择记住密码
        };
        //发送请求
        $.ajax({
            url:"/users/login/",  //登录请求地址
            type:"POST",
            data:JSON.stringify(sDataParams),
            contentType:"application/json;charset=utf-8",
            success:function (res) {
                if(res.errno==="200"){
                    message.showSuccess("恭喜登陆成功");
                    setTimeout(function(){
                        // window.location.href = document.referrer;  // 登录成功后跳转到登录界面  document.referrer  回到上一个页面
                        window.location.href = '/news/index/';  // 登录成功后跳转到index页面
                        // let sCurrentUrl = $(location).attr("href");  //获取到当前的url
                        // if (sCurrentUrl.indexOf("?next=") !== -1){  //判断url中是否有？next=/admin/这类的跳转地址
                        //     let sDomain = window.location.origin;  //获取到当前的url中的域名
                        //     window.location.href = sDomain + sCurrentUrl.split("=")[1];  //拼接跳转页面
                        // }else{
                        //     // window.location.href = document.referrer;  // 登录成功后跳转到登录界面  document.referrer  回到上一个页面
                        //     window.location.href = '/news/index/'
                        // }

                    },800);
                }else{
                    message.showError("登录失败"+res.errmsg)
                }
            },
            error:function () {
                message.showError("注册ajax,服务器超时，请重试")
            }
    })
    });

});
