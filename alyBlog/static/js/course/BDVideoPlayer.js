$(function () {
    let $courseData = $(".course-data");  //百度云VOD API接口标签
    let $videoUrl = $courseData.data('video-url');   //视频url
    let $coverUrl = $courseData.data('cover-url');   //封面url

    let player = cyberplayer('course-video').setup({
        width: '100%',// 宽度百分比（父元素宽度要有），可以是固定宽度
        height: 650, // 高度
        file: $videoUrl,  // 视频url
        image: $coverUrl,   // 封面url
        autostart: false,   //是否自动播放
        stretching: "uniform", //拉伸设置
        repeat: false,  // 是否重复播放
        volume: 100,    //音量大小（0-100）
        controls: true, //控制是否显示
        // logo: { // logo设置
        // linktarget: "_blank",
        // margin: 8,
        // hide: false,
        // position: "top-right", // 位置
        // file: "./img/logo.png" // 图片地址
        // },
        ak: '41f7e2ac93d248c3ad602f2a91e79cd5',
    })
});
