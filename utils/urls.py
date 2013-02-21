#-*- encoding:utf-8 -*-
from tornado import web
from views import blog, upload

urls = [
    web.URLSpec(r"/", blog.IndexHandler, name="index"),
    web.URLSpec(r"/p/(\d+)", blog.IndexHandler, name='indexpage'),
    web.URLSpec(r"/t/([^\/]+)/(\d+)", blog.TagHandler, name="tag"),
    web.URLSpec(r"/find", blog.FindHandler, name="find"),
    web.URLSpec(r"/date/([^\/]+)/(\d+)", blog.MonthHandler, name="month"),
    web.URLSpec(r"/a/(\d+)", blog.ArticleHandler, name="article"),
    web.URLSpec(r"/godlogin", blog.LoginHandler, name="login"),
    web.URLSpec(r"/godadd", blog.AddHandler, name="add"),
    web.URLSpec(r"/godmodify/(\d+)", blog.ModifyHandler, name="modify"),
    web.URLSpec(r"/goddel/(\d+)", blog.DelHandler, name="del"),
    web.URLSpec(r"/godupload", upload.UploaderHandler, name="upload"),
    web.URLSpec(r"/delfile/(.*)", upload.DelfileHandler, name="delfile"),
    web.URLSpec(r"/feed", blog.FeedsHandler, name="feeds"),
    web.URLSpec(r"/upload/(.*)", blog.UploadFileHandler, name='uploadfile')
]
