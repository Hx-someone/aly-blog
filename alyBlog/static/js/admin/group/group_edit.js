$(function () {

    //文档删除
    let $delBtn = $(".btn-del");
    $delBtn.click(function () {
        let _this = this;
        let sGroupId = $(this).data("group-id");
        let sGroupName = $(this).data("group-name");
        fAlert.alertConfirm({
            title: "确定删除"+ sGroupName + "权限组吗？",
            type: "error",
            confirmButtonText: "确认删除",
            cancelButtonText: "取消",
            confirmCallback: function confirmCallback() {
                $.ajax({
                    url: "/admin/group/edit/" + sGroupId + '/',
                    type: "DELETE",
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "200") {
                            message.showSuccess("成功删除" + sGroupName +"权限组！");
                            $(_this).parents("tr").remove()
                        } else {
                            swal.showInputError("删除失败：" + res.errmsg);
                        }
                    })
                    .fail(function () {
                        message.showError("服务器超时，请重试！")
                    })


            }
        })


    });




});