$(function () {
    let $startTime = $("input[name=start_time]");
    let $endTime = $("input[name=end_time]");
    const config = {

        autoclose: true,// 自动关闭

        format: 'yyyy/mm/dd',// 日期格式

        language: 'zh-CN',// 选择语言为中文

        showButtonPanel: true,// 优化样式

        todayHighlight: true, // 高亮今天

        calendarWeeks: true,// 是否在周行的左侧显示周数

        clearBtn: true,// 清除

        startDate: new Date(1900, 10, 1),// 0 ~11  网站上线的时候

        endDate: new Date(), // 今天
    };
    $startTime.datepicker(config);
    $endTime.datepicker(config);


    //文档删除
    let $delBtn = $(".btn-del");
    $delBtn.click(function () {
        let _this = this;
        let sDocId = $(this).data("doc-id");
        fAlert.alertConfirm({
            title: "确定删除该文档吗？",
            type: "error",
            confirmButtonText: "确认删除",
            cancelButtonText: "取消",
            confirmCallback: function confirmCallback() {
                $.ajax({
                    url: "/admin/doc/edit/" + sDocId + '/',
                    type: "DELETE",
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "200") {
                            message.showSuccess("成功删除文档！");
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