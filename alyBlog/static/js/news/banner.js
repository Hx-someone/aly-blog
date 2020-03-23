$(function () {
    // 新闻轮播图功能
    fn_load_banner();

    let $banner = $('.banner');
    let $picLi = $(".banner .pic li");
    let $prev = $('.banner .prev');
    let $next = $('.banner .next');
    let $tabLi = $('.banner .tab li');
    let index = 0;

    // 小原点
    $tabLi.click(function () {
        index = $(this).index();
        $(this).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    });


    // 点击切换上一张
    $prev.click(function () {
        index--;
        if (index < 0) {
            index = $tabLi.length - 1
        }
        $tabLi.eq(index).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    }).mousedown(function () {
        return false
    });

    //切换下一张
    $next.click(function () {
        auto();
    }).mousedown(function () {
        return false
    });


    //  图片向前滑动
    function auto() {
        index++;
        index %= $tabLi.length;
        $tabLi.eq(index).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(3000).siblings('li').fadeOut(3000);
    }

    // 定时器
    let timer = setInterval(auto, 2000);
    $banner.hover(function () {
        clearInterval(timer)
    }, function () {
        auto();
    });

    function fn_load_banner() {
        $.ajax({
            url: "/news/banner/",  // url尾部需要添加/// 请求地址
            type: "GET",// 请求方式
            async: false  //关闭异步
        })
            .done(function (res) {
                if (res.errno === "200") {
                    let content = ``;
                    let tab_content = ``;   //按钮
                    res.data.banner_list.forEach(function (one_banner, index) {
                        if (index === 0) {
                            // 需要修改 href  接收后台传来的id号 响应详情页  one_banner.news_id
                            content = `
                                <li style="display:block;"><a href="/news/${one_banner.article_id}/">
                                <img src="${one_banner.image_url}" alt="${one_banner.article_title}"></a></li>
                                `;
                            tab_content = `<li class="active"></li>`;
                        } else {
                            content = `
                                <li><a href="/news/${one_banner.article_id}/"><img src="${one_banner.image_url}" alt="${one_banner.article_title}"></a></li>
                            `;
                            tab_content = `<li></li>`;
                        }

                        $(".pic").append(content);  // 内容
                        $(".tab").append(tab_content); // 标签
                    });

                } else {
                    // 登录失败，打印错误信息
                    alert(res.errmsg);
                }
            })
            .fail(function () {
                alert('服务器超时，请重试！');
            });
    }

});


