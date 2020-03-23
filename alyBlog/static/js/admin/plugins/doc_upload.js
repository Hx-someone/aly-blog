$(function () {
    let $upServerBtn = $('#upload-doc');  //获取上传按钮
    let $docUrl = $("#doc-url"); //获取到图片输入框

    //图片上传
    $upServerBtn.change(function () {
        let file = this.files[0];  //获取到文件
        let sFormData = new FormData; //创建一个FormData对象
        sFormData.append("doc_file", file);  //把文件添加进去

        $.ajax({
            url: "/admin/upload/doc/",
            method: "POST",
            data:sFormData,
            processData: false,
            contentType: false,
        })
            .done(function (res) {
                if (res.errno === "200") {
                    message.showSuccess("文档上传成功");
                    let sDocUrl = res["data"]["doc_url"];
                    $docUrl.val(" ");
                    $docUrl.val(sDocUrl)  //添加新的图片url
                } else {
                    message.showError("文档上传失败")
                }
            })
            .fail(function () {
                message.showError("服务器超时，请重试！")
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
    // 将token添加到request总
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });


});