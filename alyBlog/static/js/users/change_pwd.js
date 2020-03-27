$(function () {
    let $changePwd = $(".form-contain");

    $changePwd.submit(function (res) {
        res.preventDefault();
        let $loginName = $("input[name=login_name]").val();
        let $oldPassword = $("input[name=old_password]").val();
        let $newPassword = $("input[name=new_password]").val();
        let $reNewPassword = $("input[name=re_new_password]").val();

        if($loginName === ""){
            alert("用户名不能为空");
            return
        }

        //判断旧密码、新密码和确认新密码是否为空
        if(!$oldPassword || !$newPassword || !$reNewPassword){
            alert("密码不能为空");
            return
        }

        //判断新密码是否为空和格式是否正确
        if (($oldPassword.length<6 || $oldPassword.length>20)||($newPassword.length<6 || $newPassword.length>20) || ($reNewPassword.length<6 || $reNewPassword.length>20)){
            alert("密码长度不在6-20范围内");
            return
        }
        //判断新密码确认密码是否为空，格式是否正确，是否和上一个密码一致
        let sDataParams = {
            "login_name": $loginName,
            "old_password": $oldPassword,
            "new_password": $newPassword,
            "re_new_password": $reNewPassword,
        };

        $.ajax({
            url:"/users/resetPwd/",
            type:"POST",
            data:JSON.stringify(sDataParams),
            contentType:"application/json;charset=utf-8",
            dataType:"json"
    })
            .done(function (res) {
                if (res.errno === "200"){
                    alert("恭喜您修改密码成功");
                    setTimeout(function () {
                        window.location.href = "/users/login/";
                    },1000)
                }else{
                    alert("注册失败" + res.errmsg)
                }
            })
            .fail(function () {
                alert("服务器超时，请重试")
            })
    });



});