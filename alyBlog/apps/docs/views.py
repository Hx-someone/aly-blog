from django.shortcuts import render
from django.http import Http404, FileResponse

from docs import models
from alyBlog import settings
import requests

from django.utils.encoding import escape_uri_path

from django.views import View
class IndexView(View):
    """
    create doc index view
    """
    def get(self,request):
        doc_list = models.Docs.objects.defer("create_time","update_time", "is_delete").filter(is_delete=False)
        return render(request,"docs/docDownload.html", locals())


class DocDownloadView(View):
    """
    create doc download view
    route:/docs/<int:doc_id>/
    """
    def get(self,request, doc_id):
        # 1. 从数据库中获取到id = doc_id的文件数据
        doc_file = models.Docs.objects.only("file_url").filter(is_delete=False, id=doc_id).first()

        # 2.判断文件是否为空
        if doc_file:
            # 3. 获取到文件的url地址
            file_url = doc_file.file_url

            # 4. 文档url完整路径拼接
            final_url = settings.SERVER_DOMAIN + file_url
            print("文档url:{}".format(final_url))

            # 5. 下载文档
            res = FileResponse(requests.get(final_url, stream=True)) # 以流的形式来处理下载

            suffix_name = final_url.split('.')[-1]  # 后缀名，用于判断使用什么applation

            # 6. 判断后缀名是否为空
            if not suffix_name:
                return Http404("文档不存在！")
            else:
                suffix_name = suffix_name.lower()

                # 7. 根据不同的文档格式，添加请求头信息
                if suffix_name == "pdf":
                    res['Content-type'] = 'application/pdf'
                elif suffix_name == "doc":
                    res['Content-type'] = 'application/msowrd'
                # 其他的后面添加
                else:
                    return Http404("文档不存在！")

                # 8. 添加下载文档名
                file_name = final_url.split("/")[-1]   # 文件名
                doc_name = escape_uri_path(file_name)   # 对文件名进行编码

                # 9. 添加到请求头里面
                # attachment  保存  inline 直接打开
                res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_name)

                # 10. 返回数据
                return res

        else:
            return Http404("文档不存在！")
