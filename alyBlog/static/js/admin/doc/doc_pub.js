$(function () {
    // 点击按钮实现保存
    let $docBtn = $('#btn-pub-doc');
    $docBtn.click(function () {
        let doc_id = $(this).data('doc-id');
        // 判断文档标题是否为空
        let sTitle = $("#doc-title").val();  // 获取文件标题
        if (!sTitle) {
            message.showError('请填写文档标题！');
            return
        }

        // // 判断文档作者id是否为空
        // let sAuthor = $("#doc-author").data("author-id");  // 获取文档作者id
        // if (!sAuthor) {
        //     message.showError('请填写文档作者！');
        //     return
        // }


        // 判断文档描述是否为空
        let sDigest = $("#doc-digest").val();  // 获取文档描述
        if (!sDigest) {
            message.showError('请填写文档简介！');
            return
        }

        // 判断文档缩略图url是否为空
        let sImageUrlInput = $("#image-thumbnail-url");
        let sImageUrl = sImageUrlInput.val();
        if (!sImageUrl) {
            message.showError('请上传文档缩略图');
            return
        }

        // 判断文档url是否为空
        let sDocUrlInput = $("#doc-url");
        let sDocUrl = sDocUrlInput.val();
        if (!sDocUrl) {
            message.showError('请上传文档或输入文档地址');
            return
        }


        let data = {
            "title": sTitle,
            "digest": sDigest,
            "image_url": sImageUrl,
            "file_url": sDocUrl,
        };

        $.ajax({

            url: doc_id ? '/admin/doc/edit/' + doc_id + '/' : '/admin/doc/pub/',
            type: doc_id ? 'PUT' : 'POST',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "200") {
                    if (doc_id) {
                        fAlert.alertNewsSuccessCallback("文档更新成功", '跳到文档管理页', function () {
                            window.location.href = '/admin/doc/'
                        });

                    } else {
                        fAlert.alertNewsSuccessCallback("文档发布成功", '跳到文档管理页', function () {
                            window.location.href = '/admin/doc/'
                        });
                    }
                } else {
                    fAlert.alertErrorToast(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });

    });






});
