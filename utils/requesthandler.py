#!/usr/bin/env python
# encoding: utf-8

from tornado import web
from utils.func import fetchall
import psycopg2, urllib, urlparse

db = psycopg2.connect(host='localhost', database='pitaya', user='postgres', password='', port=5432)

class BaseHandler(web.RequestHandler):
    """
    基础handler
    """

    @property
    def db(self):
        # Create a database connection when a request handler is called
        # and store the connection in the application object.
        return db

    def initialize(self):
        """
        初始化
        """
        self.d = {}

    def prepare(self):
        """
        设置islogin变量
        """
        self.d['islogin'] = self.islogin()

    def set_session(self, key, value):
        """
        设置session
        """
        self.set_secure_cookie(key, value, expires_days=None)

    def get_session(self, key):
        """
        获取session
        """
        return self.get_secure_cookie(key)

    def islogin(self):
        """
        判断是否已经登陆
        """
        if self.get_session('islogin') == 'yes':
            return True
        else:
            return False

    def set_status(self, status_code):
        '''
        解决因为数据库操作错误导致的全局500错误
        '''
        if status_code == 500:
            try:
                self.db.rollback()
            except:
                pass

        web.RequestHandler.set_status(self, status_code=status_code)

    def on_finish(self):
        pass

class BlogHandler(BaseHandler):
    def prepare(self):
        '''设置tags的列表'''
        super(BlogHandler, self).prepare()
        self.d['tags_list'] = self.get_tags()
        cur = self.db.cursor()
        cur.execute('SELECT * FROM dates ORDER BY month')
        self.d['months_list'] = fetchall(cur)  # 全部months的列表
        self.d['urlfor'] = self.urlfor

    def urlfor(self, *args, **kwargs):
        """生成url

        :*args: 发送给reverse_url
        :**kwargs: 生成url query
        :returns: url地址

        """
        url = self.reverse_url(*args)
        pr = list(urlparse.urlparse(url))
        for key in kwargs.keys():
            if type(kwargs[key]) == unicode:
                kwargs[key] = kwargs[key].encode('utf-8')
        pr[4] = urllib.urlencode(kwargs)
        return urlparse.ParseResult(*pr).geturl()

    def get_tags(self, sort=None):
        '''
        获取全部的tags列表
        '''
        cur = self.db.cursor()
        cur.execute('SELECT max(count) AS maxcount FROM tags;')
        rs = cur.fetchone()
        if rs:
            max_count = rs[0]
        else:
            return []  # 如果rs为None说明没有tag记录，直接返回

        if sort:
            cur.execute('SELECT * FROM tags ORDER BY count %s' % (sort))  # 根据sort的值排序
            tmprs = fetchall(cur)
        else:
            cur.execute('SELECT * FROM tags')
            tmprs = fetchall(cur)

        rs = []
        for t in tmprs:  # 添加每个tags的文字大小
            if t['tag'] == '':
                continue

            if t['count'] > 100:
                t['size'] = 30
            elif max_count > 100:
                t['size'] = t['count'] / 100.0 * 18 + 12
            else:
                t['size'] = 1.0 * t['count'] / max_count * 18 + 12
            rs.append(t)
        return rs


class AuthBlogHandler(BlogHandler):
    def prepare(self):
        super(AuthBlogHandler, self).prepare()  # 执行父类的prepare
        if self.islogin() != True:
            return self.redirect(self.reverse_url('login'))  # 转到登陆界面
