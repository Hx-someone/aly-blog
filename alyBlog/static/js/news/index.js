$(function () {
    let iPage = 1;  // 设定默认的page页码为1
    let sCurrentTagId = 0; // 设定默认的tag_id为0
    let $newsList = $(".news-nav ul li"); //获取到标签栏
    let iTotalPage = 1;  //设定默认的总页数为1
    let bIsLoadData = true;   //是否正在向后端传递参数

    fn_load_content();   //调用向后端请求数据函数

    $newsList.click(function () {
        //点击分类标签，则为点击的标签加上一个class属性为active
        //冰衣橱其他兄弟元素的上的值为active的class属性
        $(this).addClass("active").siblings("li").attr("active");
        //获取绑定在当前选中分类上的data-id属性值
        let sClickTagId = $(this).children("a").attr("data-id");

        if (sClickTagId !== sCurrentTagId) {
            sCurrentTagId = sClickTagId; //记录当前的分类id
            iPage = 1;
            iTotalPage = 1;
            fn_load_content()
        }

    });

    // 滚动鼠标动态加载数据
    $(window).scroll(function () {
        // 浏览器窗口高度
        let showHeight = $(window).height();

        //整个网页的高度
        let pageHeight = $(document).height();

        //页面可以滚动的距离
        let canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少，整个是睡着页面滚动实时变化的
        let nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 200) {
            //判断页数，去更新新闻数据
            if (!bIsLoadData) {
                bIsLoadData = true;
                //如果当前页面数据如果小于总页数，那么才去加载数据
                if (iPage < iTotalPage) {
                    iPage += 1;
                    $(".btn-more").remove(); //删除标签
                    //去加载数据
                    fn_load_content()
                } else {
                    message.showSuccess("已经全部加载，没有更多内容了！");
                    $(".btn-more").remove(); //删除标签
                    $(".news-list").append($('<a href="javascript:void(0)" class="btn-more">已全部加载 </a>'))
                }
            }

        }
    });


    // 向前端发送请求获取数据
    function fn_load_content() {
        //构建参数
        let sDataParams = {
            "page": iPage,
            "tag_id": sCurrentTagId,
        };

        //发送ajax请求获取数据
        $.ajax({
            url: "/news/article_list",
            type: "GET",
            data: sDataParams,
            dataType: "json",
            success: function (res) {
                if (res.errno === "200") {
                    iTotalPage = res.data.total_page;  //获取到总页数
                    if (iPage === 1) {
                        $(".news-list").html("");
                    }
                    res.data.article.forEach(function (one_article) {
                        let content = `
                            <li class="news-item">
                                <a href="/news/${ one_article.id }/" class="news-thumbnail" 
                                target="_blank">
                                    <img src="${ one_article.image_url }" alt="${ one_article.title }" title="${ one_article.title }">
                                </a>
                                <div class="news-content">
                                    <h4 class="news-title">
                                        <a href="/news/${ one_article.id }/">${ one_article.title }</a>
                                    </h4>
                                    <p class="news-details">${ one_article.digest }</p>
                                    <div class="news-other">
                                        <ul class="bottom-info">
                                            <li><i class="iconfont icon-shijian"></i>&nbsp;<a href="">${ one_article.update_time}</a></li>
                                            <li><i class="iconfont icon-zuozhe1"></i>&nbsp;<a href="">${ one_article.author}</a></li>
                                            <li><i class="iconfont icon-comment"></i>&nbsp;<a href="">${ one_article.comment_num}<a></li>
                                            <li><i class="iconfont icon-yueduliang"></i>&nbsp;<a href="">${ one_article.clicks}</a></li>
                                            <li class="bottom-tag"><i class="iconfont icon-xingzhuang"></i><a href="">
${ one_article.tag_name}</a></li>
                                        </ul>
                                        
                                        
                                    </div>
                                </div>
                            </li>
                        `;
                        $(".news-list").append(content)
                    });
                    // $(".news-list").append($('<a href="javascript:void(0);" class="btn-more">点击加载更多</a>'));
                    bIsLoadData = false
                }
                else {
                    message.showError(res.errmsg)
                }
            },
            error: function () {
                message.showError("服务器请求超时，请重试")
            }


        })

    }

});