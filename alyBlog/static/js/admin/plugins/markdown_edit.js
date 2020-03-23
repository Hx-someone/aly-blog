let testEditor;
$(function () {
    $.get("{% static 'plugins/markdown_editor/examples/test.md' %}", function (md) {
        testEditor = editormd("article-content", {
            width: "98%",
            height: 730,
            path: "{% static 'plugins/markdown_editor/lib/' %}",
            markdown: md,
            codeFold: true,
            saveHTMLToTextarea: true,
            searchReplace: true,
            htmlDecode: "style,script,iframe|on*",
            emoji: true,
            taskList: true,
            tocm: true,         			// Using [TOCM]
            tex: true,                   // 开启科学公式TeX语言支持，默认关闭
            flowChart: true,             // 开启流程图支持，默认关闭
            sequenceDiagram: true,       // 开启时序/序列图支持，默认关闭,
            imageUpload: true,
            imageFormats: ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
            imageUploadURL: "{% url 'admin:article_upload_image' %}",
            // {#          onload: function () {#}
            // {#            console.log('onload', this);#}
            // {##}
            // {#          },#}
            /**设置主题颜色 把这些注释去掉主题就是黑色的了*/
            // {#          editorTheme: "pastel-on-dark",#}
            // {#          theme: "dark",#}
            // {#          previewTheme: "dark"#}
        });
    });
});