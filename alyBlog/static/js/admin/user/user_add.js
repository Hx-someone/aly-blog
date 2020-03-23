$(function () {
    // 获取修改之前的值
    let $oldIsStaff = $("input[name='login_admin']:checked").val();
    let $oldIsSuperuser = $("input[name='is_superuser']:checked").val();
    let $oldIsActive = $("input[name='is_active']:checked").val();
    let $oldGroups = $("#add_group").val();


    let $usersBtn = $("#btn-edit-user");
    $usersBtn.click(function () {
        // 判断用户信息是否修改
        // 获取修改之后的值

        let sNewIsStaff = $("input[name='login_admin']:checked").val();
        let sNewIsSuperuser = $("input[name='is_superuser']:checked").val();
        let sNewIsActive = $("input[name='is_active']:checked").val();
        let sNewGroups = $("#add_group").val();

        if ($oldIsStaff === sNewIsStaff && $oldIsSuperuser === sNewIsSuperuser
            && $oldIsActive === sNewIsActive &&
            (JSON.stringify($oldGroups) === JSON.stringify(sNewGroups))) {
            message.showError('用户信息未修改！');
            return
        }

        // 获取user-id
        let sUserId = $(this).data("user-id");
        let sDataParams = {
            "is_staff": sNewIsStaff,
            "is_superuser": sNewIsSuperuser,
            "is_active": sNewIsActive,
            "groups": sNewGroups

        };

        $.ajax({
            url: '/admin/user/edit/' + sUserId + '/',
            type: 'PUT',
            data: JSON.stringify(sDataParams),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "200") {
                    fAlert.alertNewsSuccessCallback("用户信息更新成功", '跳到用户管理页', function () {
                        window.location.href = '/admin/user/'
                    })
                } else {
                    fAlert.alertErrorToast(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });

    });


});