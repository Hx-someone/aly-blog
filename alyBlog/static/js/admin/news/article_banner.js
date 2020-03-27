$(function () {
    let $delBtn = $(".del-btn");  //删除按钮
    let $UpdateBtn = $(".update-btn");  //更新按钮
    let $bannerImage = $(".banner-image"); //图片元素
    let $addBtn = $("#banner-add-btn"); //添加按钮
    let $banner = $(".banner");  //整个轮播图列表
    let $imageUpload = $("input[name=banner-image-select]");// 轮播图输入框


    // 轮播图删除
    $delBtn.click(function () {
        console.log(11111);
        let _this = this;
        let sBannerId = $(this).parents("li").data("banner-id");
        console.log(sBannerId);

        fAlert.alertConfirm({  //弹窗
                title: "确定删除该文章轮播图吗？",
                type: "error",
                confirmButtonText: "确认删除",
                cancelButtonText: "取消",
                confirmCallback: function confirmCallback() {
                    $.ajax({
                        url: "/admin/article/banner/" + sBannerId + "/",
                        type: "DELETE",
                        dataType: "json",
                    })
                        .done(function (res) {
                            if (res.errno === "200") {
                                message.showError("成功删除文章轮播图！");
                                $(_this).parents("li").remove()
                            } else {
                                swal.showInputError("删除失败：" + res.errmsg);
                            }
                        })
                        .fail(function () {
                            message.showError("服务器超时，请重试！")
                        })
                }
            }
        )
    });


    //轮播图修改
    $UpdateBtn.click(function () {
        let _this = this;
        let sImageUrl = $(this).parents("li").find(".banner-image").attr("src"); // 获取到当前的图片url
        let sBannerPriority = $(this).parents("li").find("#priority").val();  // 获取到当前的轮播图优先级
        let sBannerId = $(this).parents("li").data("banner-id"); //获取到当前的轮播图id

        let sOldImageUrl = $(_this).data("image-url");  //获取到更新前的image_url
        let sOldPriority = $(_this).data("priority");

        //判断更新后的url是否为空
        if (!sImageUrl) {
            message.showError("轮播图url不能为空");
            return
        }

        if (!sBannerPriority) {
            message.showError("轮播图优先级不能为空");
            return
        }

        if (sImageUrl === sOldImageUrl && sBannerPriority === sOldPriority) {
            message.showError("轮播图未改变");
            return
        }

        let sDataParams = {
            "image_url": sImageUrl,
            "priority": sBannerPriority,
            "banner_id": sBannerId,

        };

        $.ajax({
            url: "/admin/article/banner/" + sBannerId + "/",
            type: "PUT",
            data: JSON.stringify(sDataParams),
            contentType: "application/json;charset=utf8",
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "200") {
                    message.showSuccess("轮播图更新成功")
                } else {
                    message.showError("轮播图更新失败：" + res.message)
                }
            })
            .fail(function () {
                message.showError("服务器超时，请重试！")
            })
    });


    //轮播图上传调用
    $bannerImage.click(function () {
        $(this).prev().click()
    });

    //轮播图上传
    $imageUpload.change(function () {
        let _this = this;
        let file = this.files[0];  //获取到文件
        let sFormData = new FormData; //创建一个FormData对象
        sFormData.append("image_file", file);  //把文件添加进去

        $.ajax({
            url: "/admin/article/images/",
            method: "POST",
            data: sFormData,
            processData: false,
            contentType: false,
        })
            .done(function (res) {
                if (res.errno === "200") {
                    message.showSuccess("图片上传成功");
                    let sImageUrl = res["data"]["image_url"];
                    $(_this).next().attr("src", sImageUrl);
                } else {
                    message.showError("图片上传失败")
                }
            })
            .fail(function () {
                message.showError("服务器超时，请重试！")
            })

    });

    //轮播图添加
    $addBtn.click(function () {
        if ($banner.find('li').length < 6) {
            window.location.href = '/admin/article/banner/add/';
        } else {
            message.showError("最多只能添加6个轮播图")
        }
    });


});


