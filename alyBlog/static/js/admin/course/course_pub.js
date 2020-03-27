$(function () {

    // 点击按钮实现保存
    let $courseBtn = $('#btn-pub-course');
    $courseBtn.click(function () {
        let sCourseId = $(this).data('course-id');
        // 判断课程名是否为空
        let sName = $("#course-name").val();
        if (!sName) {
            message.showError('请填写课程名！');
            return
        }

        // 判断课程简介是否为空
        let sBrief = $("#course-brief").val();
        if (!sBrief) {
            message.showError('请填写课程简介！');
            return
        }


        // 判断课程分类是否为空
        let sCategory = $("#course-category").val();  // 获取文档描述
        if (!sCategory || sCategory==="0") {
            message.showError('请选择课程分类！');
            return
        }

        // 判断任课教师是否为空
        let sTeacher = $("#course-teacher").val();  // 获取文档描述
        if (!sTeacher || sTeacher==="0") {
            message.showError('请选择任课教师！');
            return
        }


        // 判断课程封面url是否为空
        let sImageUrlInput = $("#image-url");
        let sImageUrl = sImageUrlInput.val();
        if (!sImageUrl) {
            message.showError('请上传课程封面');
            return
        }

        // 判断视频URL是否为空
        let sVideoUrlInput = $("#video-url");
        let sVideoUrl = sVideoUrlInput.val();
        if (!sVideoUrl) {
            message.showError('请上传课程视频');
            return
        }

        // 判断课程大纲是否为空
        let sOutline = $(".markdown-body").html();
        if (!sOutline) {
            message.showError('课程大纲不能为空');
            return
        }


        let data = {
            "name": sName,
            "brief": sBrief,
            "category": sCategory,
            "teacher": sTeacher,
            "cover_url": sImageUrl,
            "video_url": sVideoUrl,
            "outline": sOutline,
        };

        $.ajax({

            url: sCourseId ? '/admin/course/edit/' + sCourseId + '/' : '/admin/course/pub/',
            type: sCourseId ? 'PUT' : 'POST',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "200") {
                    if (sCourseId) {
                        fAlert.alertNewsSuccessCallback("课程更新成功", '跳到课程管理页', function () {
                            window.location.href = '/admin/course/'
                        });

                    } else {
                        fAlert.alertNewsSuccessCallback("课程发布成功", '跳到课程管理页', function () {
                            window.location.href = '/admin/course/'
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
