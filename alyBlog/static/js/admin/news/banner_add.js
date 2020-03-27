$(function () {
    let $saveBtn = $("#save-btn");  //保存按钮
    let $imageUpload = $("input[name=banner-image-select]"); // 图片输入框
    let $bannerImage = $(".banner-image");//图片img
    let $tagSelect = $("#tag-select"); //文章标签分类元素
    let $articleSelect = $("#article-select"); //文章元素

    //点击元素分类时显示对应的文章

    // 选择文章不同类别，获取相应的文章
    $tagSelect.change(function () {
        // 获取当前选中的下拉框的value
        let sTagId = $(this).val();

        // 标签为0时文章也显示0
        if (sTagId === '0') {
            $articleSelect.children('option').remove();
            $articleSelect.append(`<option value="0">--请选择文章--</option>`);
            return
        }

        // 根据文章分类id向后端发起get请求
        $.ajax({
            // 请求地址
            url: "/admin/tags/" + sTagId + "/article/",  // url尾部需要添加/
            // 请求方式
            type: "GET",
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "200") {

                    $articleSelect.children('option').remove();
                    $articleSelect.append(`<option value="0">--请选择文章--</option>`);
                    res.data.articles.forEach(function (article) {
                        let content = `<option value="${article.id}">${article.title}</option>`;
                        $articleSelect.append(content)
                    });

                } else {
                    // swal.showInputError(res.errmsg);
                    fAlert.alertErrorToast(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });

    });


    //添加轮播图
    $saveBtn.click(function () {
        let sArticleTagId = $("#tag-select").val(); //文章类型
        let sArticleId = $("#article-select").val();//文章
        let sPriority = $("#priority").val();//轮播图优先级
        let sImageUrl = $(".banner-image").attr("src"); //获取图片url


        //判断url是否设置为默认的图片
        if (sImageUrl === '/static/images/banner_default.png') {
            message.showError('轮播图不能为默认图片');
            return
        }

        //判断优先级是否在优先级表中
        if (!$.inArray(sPriority, ["1", "2", "3", "4", "5", "6"])) {
            swal.showInputError("优先级必须在1,2,3中选择");
        }


        //轮播图、文章类型、文章、优先级任意一个都不能为假
        if (sArticleTagId !== "0" && sArticleId !== "0" && sPriority !== "0" && sImageUrl) {
            let sDataParams = {
                "image_url": sImageUrl,
                "article_id": sArticleId,
                "priority": sPriority,
            };
            console.log(sDataParams);

            $.ajax({
                url: "/admin/article/banner/add/",
                type: "POST",
                data: JSON.stringify(sDataParams),
                contentType: "application/json;charset=utf8",
                dataType: "json",
            })
                .done(function (res) {
                    if (res.errno === "200") {
                        message.showSuccess("轮播图添加成功");
                        setTimeout(function () {
                            window.location.href = "/admin/article/banner";
                        }, 800)
                    } else {
                        message.showError("轮播图添加失败：" + res.errmsg)
                    }
                })
                .fail(function () {
                    message.showError("服务器超时，请重试")
                })
        }
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



});