$(function () {

    //删除用户
    let $userDel = $(".btn-del");  // 1. 获取删除按钮
    $userDel.click(function () {   // 2. 点击触发事件
        let _this = this;
        let sUserId = $(this).parents('tr').data('user-id');
        let sUserName = $(this).parents('tr').data('user-name');

        fAlert.alertConfirm({
            title: `确定删除 ${sUserName} 这个用户吗？`,
            type: "error",
            confirmText: "确认删除",
            cancelText: "取消删除",
            confirmCallback: function confirmCallback() {

                $.ajax({
                    url: "/admin/user/edit/" + sUserId + "/",
                    type: "DELETE",
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "200") {
                            message.showSuccess("用户删除成功");
                            $(_this).parents('tr').remove();
                        } else {
                            swal.showInputError(res.errmsg);
                        }
                    })
                    .fail(function () {
                        message.showError('服务器超时，请重试！');
                    });
            }
        });
    });

});
