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
                        alert("服务器超时，请重试！")
                    })


            }
        })


    });



    // 获取cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // 添加token到request中
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
});