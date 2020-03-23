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



    // 删除标签
    let $articleDel = $(".btn-del");  // 1. 获取删除按钮
    $articleDel.click(function () {   // 2. 点击触发事件
        let _this = this;
        let sArticleId = $(this).data('article-id');
        swal({
            title: "确定删除这篇文章吗?",
            text: "删除之后，将无法恢复！",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定删除",
            cancelButtonText: "取消",
            closeOnConfirm: true,
            animation: 'slide-from-top',
        }, function () {

            $.ajax({
                // 请求地址
                url: "/admin/article/edit/" + sArticleId + "/",  // url尾部需要添加/
                // 请求方式
                type: "DELETE",
                dataType: "json",
            })
                .done(function (res) {
                    if (res.errno === "200") {
                        // 更新标签成功
                        message.showSuccess("文章删除成功");
                        $(_this).parents('tr').remove();
                    } else {
                        swal({
                            title: res.errmsg,
                            type: "error",
                            timer: 1000,
                            showCancelButton: false,
                            showConfirmButton: false,
                        })
                    }
                })
                .fail(function () {
                    message.showError('服务器超时，请重试！');
                });
        });

    });

});