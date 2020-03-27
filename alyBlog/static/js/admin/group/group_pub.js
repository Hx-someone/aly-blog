$(function () {

    let $groupBtn = $('#btn-pub-group');
    $groupBtn.click(function () {

        //判断组名是否为空
        let sName = $('#group-name').val();

        if (!sName) {
            message.showError('组名不能为空！！');
            return
        }
        // 判断权限
        let sGroupPermission = $('#group-permissions').val();
        if (!sGroupPermission || sName === []) {
            message.showError('请选择你的权限');
            return
        }
        let sGroupId = $(this).data('group-id');


        let data = {
            'name': sName,
            'group_permission': sGroupPermission
        };

        $.ajax({
            url: sGroupId ? '/admin/group/edit/' + sGroupId + '/' : '/admin/group/add/',
            type: sGroupId ? 'PUT' : 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
        })
        // 回调
            .done(function (res) {
                if (res.errno === '200') {
                    if (sGroupId) {
                        message.showSuccess("用户组更新成功");
                        fAlert.alertNewsSuccessCallback('用户组更新成功', "跳转到用户首页", function () {
                            window.location.href = '/admin/group/'
                        });

                    } else {
                        message.showSuccess("用户组创建功");
                        fAlert.alertNewsSuccessCallback('用户组创建', "跳转到用户首页", function () {
                            window.location.href = '/admin/group/'
                        });
                    }
                }else{
                    if(sGroupId){
                        message.showError("用户组更新失败")
                    }else{
                        message.showError("用户组创建失败")
                    }

                }
            })
            .fail(function () {
                message.showError("服务器超时，请重试")
            })
    });

});

