$(function () {
    let sdk = baidubce.sdk;
    let VodClient = sdk.VodClient;

    const CONFIG = {
        endpoint: 'http://vod.bj.baidubce.com',	// 默认区域名
        credentials: {
            ak: '41f7e2ac93d248c3ad602f2a91e79cd5',	 // 填写你的百度云中ak和sk
            sk: '19de5b742a254783aa534a514d36d628'    // 在百度vod 安全认证里面
        }
    };

    // 百度云vod域名在多媒体/全局设置/发布设置里面
    let BAIDU_VOD_DOMAIN = 'kc3nrwmns1rqrn2kzu6.exp.bcevod.com';	// 百度云VOD域名

    const CLIENT = new VodClient(CONFIG);


    $(function () {

        // 上传s视频至服务器
        let sUploadVideo = $("#upload-video");
        let sInputVideoUrl = $("#video-url");
        sUploadVideo.change(function () {

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


            let sVideoFile = this.files[0];   // 获取文件
            let sVideoFileType = sVideoFile.type;

            // 调用百度云VOD接口
            let blob = new Blob([sVideoFile], {type: sVideoFileType});

            CLIENT.createMediaResource(sName, sBrief, blob)
            // Node.js中<data>可以为一个Stream、<pathToFile>；在浏览器中<data>为一个Blob对象
                .then(function (response) {
                    // 上传完成
                    message.showSuccess("视频上传成功");
                    let sMediaId = response.body.mediaId;
                    console.log('媒资ID为：', sMediaId);
                    let sVideoUrl = 'http://' + BAIDU_VOD_DOMAIN + '/' + sMediaId + '/' + sMediaId + '.m3u8';
                    sInputVideoUrl.val('');
                    sInputVideoUrl.val(sVideoUrl);

                })
                .catch(function (error) {
                    console.log(error);   // 上传错误
                    message.showError(error)
                });

        });


    });


});

