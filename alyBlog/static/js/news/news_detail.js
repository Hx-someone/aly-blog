$(function () {
    // 未登录提示框
    let $loginComment = $('.please-login-comment input');  //获取请登录框
    let $sendComment = $('.logged-comment .comment-btn');  //获取到评论按钮
    let $commentCount = $('.new-comment .comment-count');   //获取到评论条数


    $('.comment-list').delegate('a,input', 'click', function () {  //delegate委托事件
        let sClassValue = $(this).prop('class'); //取出class属性值
        if (sClassValue.indexOf('reply_a_tag') >= 0) {
            $(this).next().toggle(); //交叉显示，点击时显示，再次点击就不显示
        }

        if (sClassValue.indexOf("reply_cancel") >= 0) {
            $(this).parent().toggle();//交叉显示，点击时显示，再次点击就不显示
        }

        //回复评论
        if (sClassValue.indexOf('reply_btn') >= 0) {
            //进行发送ajax请求数据给后端
            let $this = $(this);  //获取当前点击回复
            let article_id = $this.parent().attr("article_id");  //上一个评论的的文章id
            let parent_id = $this.parent().attr("comment_id");   //上一个评论的id
            let content = $this.prev().val();//评论内容

            //判断评论内容是是否为空
            if (!content) {
                alert("评论内容为空，请重新输入");
            }

            //构造ajax请求参数
            let sDataParams = {
                "content": content,
                "parent_id": parent_id,
            };

            //发送ajax请求
            $.ajax({
                url: '/news/' + article_id + "/comments/",
                type: "POST",
                contentType: "application/json, charset=utf-8",
                data: JSON.stringify(sDataParams),
                dataType: 'json',
            })
                .done(function (res) {
                    if (res.errno === "200") {
                        let comment = res.data.data;
                        let html_content = ``;
                        $commentCount.empty();  //移除文本内容
                        $commentCount.text(res.data.count); //添加新的评论数


                        html_content += `
                        <li class="comment-item">
                            <div class="comment-info clearfix">
                                <img src="../../static/images/avatar.jpeg" alt="avatar" class="comment-avatar">
                                <span class="comment-user">${ comment.author }</span>
                                <span class="comment-pub-time">${ comment.update_time }
                            </div>
                            <div class="comment-content">${ comment.content }</div>
                            <div class="parent_comment_text">
                                <div class="parent_username">${ comment.parent.author }</div>
                                <br/>
                                <div class="parent_content_text">${ comment.parent.content }</div>
                            </div>
                            
                        
                            <div class="comment_time left_float">${comment.update_time}</div>
                            <a href="javascript:void(0);" class="reply_a_tag right_float">回复</a>
                            <form class="reply_form left_float" comment_id="${comment.comment_id}" article_id="${comment.article_id}">
                                <textarea class="reply_input"></textarea>
                                <input type="button" value="回复" class="reply_btn right_float">
                                <input type="reset" name="" value="取消" class="reply_cancel right_float">
                            </form>
                        </li>`;

                        $('.comment-list').prepend(html_content);
                        $this.prev().val("");   //清空输入框
                        $this.parent().hide();   //关闭评论框
                    } else if (res.errno = "4101") {
                        alert("请登录后再评论");
                        setTimeout(function () {
                            //重定向到登录界面
                            window.location.href = "/users/login"
                        }, 800)
                    } else {
                        alert(res.errmsg)
                    }
                })
                .fail(function () {
                    alert("服务器超时，请重试！")
                })


            // 定义给后端的参数
        }
    });

    //点击评论框，重定向到用户登录页面
    $loginComment.click(function () {
        $.ajax({
            url: "/news/" + $(".please-login-comment").attr("article_id") + "/comments/",
            type: "POST",
            contentType: "applications/json, charset=utf-8",
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "4101") {
                    setTimeout(function () {
                        window.location.href = "/users/login";
                    }, 800)
                } else {
                    alert(res.message);
                }
            })
            .fail(function () {
                alert("服务器超时，请重试！");
            })
    });


    // 发表评论
    $sendComment.click(function () {
        //获取到文章的id,评论的id,评论内容
        let $this = $(this);
        let article_id = $this.parent().attr("article_id");
        let content = $this.prev().val();


        if (!content) {
            alert("评论内容为空，请重新输入！");
            return
        }
        let sDataParams = {
            "content": content,
        };

        $.ajax({
            url: '/news/' + article_id + "/comments/",
            type: "POST",
            contentType: "application/json, charset=utf-8",
            data: JSON.stringify(sDataParams),
            dataType: 'json',
        })
            .done(function (res) {
                if (res.errno === "200") {
                    let comment = res.data.data;
                    let html_content = ``;
                    $commentCount.empty();
                    $commentCount.text(res.data.count); //添加新的评论数

                    html_content += `
                        <li class="comment-item">
                            <div class="comment-info clearfix">
                                <img src="../../static/images/avatar.jpeg" alt="avatar" class="comment-avatar">
                                <span class="comment-user">${ comment.author }</span>
                                <span class="comment-pub-time">${ comment.update_time }</span>
                            </div>
                            <div class="comment-content">${ comment.content }</div>                          

                            <div class="comment_time left_float">${ comment.update_time }</div>
                            <a href="javascript:void(0);" class="reply_a_tag right_float">回复</a>
                            <form class="reply_form left_float" comment_id="${comment.comment_id}" article_id="${comment.article_id}">
                                <textarea class="reply_input"></textarea>
                                <input type="button" value="回复" class="reply_btn right_float">
                                <input type="reset" name="" value="取消" class="reply_cancel right_float">
                            </form>
                        </li>`;

                    $('.comment-list').prepend(html_content);
                    $this.prev().val("");   //清空输入框
                } else if (res.errno = "4101") {
                    alert("请登录后再评论");
                    setTimeout(function () {
                        //重定向到登录界面
                        window.location.href = "/users/login";
                    }, 800)
                } else {
                    alert(res.errmsg)
                }
            })
            .fail(function () {
                alert("服务器超时，请重试！")
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