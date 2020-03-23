$(function () {
    let $upServerBtn = $('#upload-image');  //获取上传按钮
    let $imageUrl = $("#image-url"); //获取到图片输入框
    $upServerBtn.change(function () {
        let file = this.files[0];  //获取到文件
        let sFormData = new FormData; //创建一个FormData对象
        sFormData.append("image_file", file);  //把文件添加进去

        $.ajax({
            url: "/admin/upload/images/",
            method: "POST",
            data:sFormData,
            processData: false,
            contentType: false,
        })
            .done(function (res) {
                if (res.errno === "200") {
                    message.showSuccess("图片上传成功");
                    let sImageUrl = res["data"]["image_url"];
                    $imageUrl.val(" ");
                    $imageUrl.val(sImageUrl)  //添加新的图片url
                } else {
                    message.showError("图片上传失败")
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