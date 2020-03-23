$(function () {
    let $pubArticle = $("#btn-pub-article");

    $pubArticle.click(function () {

        //判断文章标题是否为空
        let sArticleTitle = $("#article-title").val(); // 获取到文章的标题
        if (!sArticleTitle) {
            message.showError("文章标题不能为空");
            return
        }

        //判断文章摘要是否为空
        let sArticleDigest = $("#article-digest").val(); // 获取到文章摘要的值
        if (!sArticleDigest) {
            message.showError("文章摘要不能为空");
            return
        }

        //判断文章标签是否为空
        let sArticleTagId = $("#article-category").val();// 获取到文章标签id
        console.log(sArticleTagId);
        if (!sArticleTagId || sArticleTagId === 0) {
            message.showError("文章标签不能为空");
            return
        }

        //判断文章缩略图是否为空
        let sArticleImage = $("#image-url").val();// 获取到文章缩略图
        if (!sArticleImage) {
            message.showError("文章缩略图不能为空");
            return
        }

        //判断文章内容是否为空
        // let sArticleContent = $("#content").val();// 获取到文章内容
        //         // if (!sArticleContent) {
        //         //     message.showError("文章内容不能为空");
        //         //     return
        //         // }
        let sArticleContent = $(".markdown-body").html(); // 获取到文章内容
        console.log(sArticleContent);

        if (!sArticleContent || sArticleContent === '<p><br></p>') {
            message.showError('文章内容不能为空！');
            return
        }
        console.log(sArticleTagId);
        let sDataParams = {
            "title": sArticleTitle,
            "digest": sArticleDigest,
            "tag": sArticleTagId,
            "image_url": sArticleImage,
            "content": sArticleContent
        };
        let sArticleId = $(this).data("article-id");
        $.ajax({
            url: sArticleId?"/admin/article/edit/" + sArticleId + "/":"/admin/article/pub/", //有文章id就是编辑，无则是发布
            type: sArticleId?"PUT":"POST",
            data: JSON.stringify(sDataParams),
            contentType: "application/json;charset=utf8",
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "200") {
                    if(sArticleId){message.showSuccess("文章更新成功！");
                    setTimeout(function () {
                        window.location.href = "/admin/article/";
                    }, 800)
                    }else{
                        message.showSuccess("文章发布成功！");
                    setTimeout(function () {
                        window.location.reload()
                    }, 800)
                    }

                } else {
                    fAlert.alertError(res.errmsg);
                    // message.showError(res.errmsg)
                }
            })
            .fail(function () {
                message.showError("服务器超时，请重试！")
            })
    });

    // get cookie using jQuery
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

// Setting the token on the AJAX request
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
});