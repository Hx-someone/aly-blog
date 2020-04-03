$(function () {  //增删改查
    let $editBtn = $(".btn-edit");
    let $delBtn = $(".btn-del");
    let $addBtn = $("#btn-add-tag");

    //标签添加
    $addBtn.click(function () {
        fAlert.alertOneInput({
            title:"请输入新的文章标签",
            text:"输入长度请保持在20字以内",
            placeholder: "请输入新的文章标签",
            confirmCallback: function confirmCallback(inputval) {
                let sDataParams={
                    "name":inputval,
                };

                $.ajax({
                    url: "/admin/tags/",
                    type:"POST",
                    data:JSON.stringify(sDataParams),
                    contentType: "application/json;charset=utf-8",
                    dataType:"json",
                })
                    .done(function (res) {
                        if (res.errno === "200"){
                            fAlert.alertSuccessToast(inputval+ " 标签添加成功");
                            setTimeout(function () {
                                window.location.reload();
                            },1000)
                        }else{
                            swal.showInputError("添加失败：" + res.errmsg);

                        }
                    })
                    .fail(function () {
                        alert("服务器超时，请重试！")
                    })
            }



        })
    });


    //标签删除
    $delBtn.click(function () {
        let _this = this;
        let sTagId = $(this).parents("tr").data("id");
        let sTagName = $(this).parents("tr").data("name");
        fAlert.alertConfirm({  //弹窗
           title:"确定删除" + sTagName + "标签吗？",
            type:"error",
            confirmButtonText:"确认删除",
            cancelButtonText:"取消",
            confirmCallback:function confirmCallback() {
                $.ajax({
                    url:"/admin/tags/" + sTagId +"/",
                    type:"DELETE",
                    dataType:"json",
                })
                    .done(function (res) {
                        if (res.errno === "200"){
                            alert("成功删除 "+ sTagName + " 标签！");
                            $(_this).parents("tr").remove()
                        }else{
                             swal.showInputError("删除失败：" + res.errmsg);
                        }
                    })
                    .fail(function () {
                        alert("服务器超时，请重试！")
                    })
            }
            }
        )
    });


    //标签修改
    $editBtn.click(function () {
        let _this = this;
        let sTagID = $(this).parents("tr").data("id");
        let sTagName = $(this).parents("tr").data("name");
        fAlert.alertOneInput({
            title:"编辑文章标签",
            text:"您正在编辑 " + sTagName + " 标签",
            placeholder: "请输入文章标签",
            value:sTagName,
            confirmCallback:function callfirmCallback(inputval) {
                if (inputval === sTagName){
                    swal.showInputError("标签名没有改变");
                    return false
                }

                let sDataParams={
                    "name":inputval,
                };

                $.ajax({
                    url:"/admin/tags/" + sTagID + "/",
                    type:"PUT",
                    data:JSON.stringify(sDataParams),
                    contentType: "application/json;charset=utf-8",
                    dataType:"json",
                })
                    .done(function (res) {
                        if (res.errno==="200"){
                            $(_this).parents("div").parents("div").data("priority",inputval);  //更新标签
                            let sPriNum = $("#priority-num");
                             // sPriNum.text
                            // $(_this).parent("tr").data("name",inputval); //更新data-name的值没有解决
                            swal.close();
                            message.showSuccess("标签修改成功")
                        }else{
                           swal.showInputError("删除失败：" + res.errmsg);
                        }
                    })
                    .fail(function () {
                        message.showError("服务器超时，请重试！")
                    })


            }
        })
    })

    //标签查找空了再写



});