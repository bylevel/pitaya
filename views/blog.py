#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils.requesthandler import BlogHandler, AuthBlogHandler
from utils.func import Pagination, date_add, fetchall, fetchone, search
from utils.rst import html_body
from datetime import datetime
from time import time, mktime
import os, mimetypes, PyRSS2Gen, xapian


class IndexHandler(BlogHandler):
    def get(self, page=1):
        page = int(page)
        if page <= 0:
            page = 1
        pagesize = 10
        cur = self.db.cursor()
        cur.execute('SELECT count(0) as count FROM articles WHERE id != %s', (0,))
        totalrows = fetchone(cur)['count']
        cur.execute(
            'SELECT id, title, posttime, render, '
            'ARRAY('
            'SELECT tag FROM link_tags_articles WHERE link_tags_articles.article_id = articles.id'
            ') as tags '
            'FROM articles WHERE id != %s '
            'ORDER BY posttime desc OFFSET %s LIMIT %s',
            (0, (page - 1) * pagesize, pagesize))
        self.d['articles'] = fetchall(cur)
        self.d = Pagination(self.d, page, pagesize, totalrows)
        self.render('index.html', **self.d)


class TagHandler(BlogHandler):
    def get(self, tag, page=1):
        page = int(page)
        if page <= 0:
            page = 1
        pagesize = 10
        cur = self.db.cursor()
        cur.execute('SELECT count(0) as count '
                    'FROM link_tags_articles LEFT JOIN articles '
                    'ON link_tags_articles.article_id = articles.id '
                    'WHERE link_tags_articles.tag=%s', (tag,))
        totalrows = fetchone(cur).count
        self.d['tag_name'] = tag
        cur.execute(
            'SELECT articles.id, articles.title, articles.posttime, articles.render, '
            'ARRAY(SELECT tag FROM link_tags_articles as lta WHERE lta.article_id = articles.id) as tags '
            'FROM link_tags_articles LEFT JOIN articles '
            'ON link_tags_articles.article_id = articles.id '
            'WHERE link_tags_articles.tag=%s '
            'ORDER BY posttime desc OFFSET %s LIMIT %s', (tag, (page - 1) * pagesize, pagesize))
        self.d['articles'] = fetchall(cur)
        self.d = Pagination(self.d, page, pagesize, totalrows)
        self.render('tag.html', **self.d)

class FindHandler(BlogHandler):
    def get(self):
        page = int(self.get_argument('page', 1))
        if page <= 0:
            page = 1
        pagesize = 10
        keywords = self.get_argument('keywords', '')
        #如果搜索关键字为空则返回首页
        if not keywords:
            return self.redirect('/')

        #搜索结果
        matches = search.search(keywords, offset=(page-1)*10, limit=pagesize)
        ids = [m.docid for m in matches]
        ids.append(-1)
        cur = self.db.cursor()
        #取得检索总记录数
        totalrows = matches.get_matches_estimated()
        self.d['keywords'] = keywords
        cur.execute(
            'SELECT articles.id, articles.title, articles.posttime, articles.render, '
            'ARRAY(SELECT tag FROM link_tags_articles as lta WHERE lta.article_id = articles.id) as tags '
            'FROM articles '
            'WHERE id IN %s ORDER BY posttime desc', (tuple(ids),))
        self.d['articles'] = fetchall(cur)
        self.d = Pagination(self.d, page, pagesize, totalrows)
        self.render('find.html', **self.d)

class MonthHandler(BlogHandler):
    def get(self, month, page=1):
        page = int(page)
        if page <= 0:
            page = 1
        pagesize = 10
        start_date = datetime.strptime(month.encode('utf-8'), '%Y年%m月')
        if start_date.month < 12:
            stop_date = datetime(year=start_date.year,
                month=start_date.month + 1, day=1)
        else:
            stop_date = datetime(year=start_date.year + 1, month=1,
                day=1)

        cur = self.db.cursor()
        cur.execute('SELECT count(0) as count '
                    'FROM articles WHERE posttime>=%s and posttime<%s', (start_date, stop_date))
        totalrows = fetchone(cur).count
        self.d['month_name'] = month
        cur.execute('SELECT id,title,render,posttime,'
                    'ARRAY('
                    'SELECT tag FROM link_tags_articles as lta WHERE lta.article_id = articles.id'
                    ') as tags FROM articles WHERE posttime>=%s and posttime<%s '
                    'ORDER BY posttime desc OFFSET %s LIMIT %s',
            (start_date, stop_date, (page - 1) * pagesize, pagesize))
        self.d['articles'] = fetchall(cur)
        self.d = Pagination(self.d, page, pagesize, totalrows)
        self.render('month.html', **self.d)


class LoginHandler(BlogHandler):
    def get(self):
        """
        登陆
        """

        self.render('login.html', **self.d)

    def post(self):
        loginname = self.get_argument('loginname', '')  # 用户名
        loginpass = self.get_argument('loginpass', '')  # 登陆密码

        cur = self.db.cursor()
        cur.execute('SELECT password as password FROM users WHERE username = %s', (loginname,))
        user = fetchone(cur)
        if user and user.password == loginpass:
            self.set_session('islogin', 'yes')

        self.redirect('/')

        #        self.finish()


class AddHandler(AuthBlogHandler):
    """
    添加文章
    """

    def get(self):
        cur = self.db.cursor()
        cur.execute('SELECT filename FROM files '
                    'WHERE filename NOT IN (SELECT filename FROM link_files_articles)')
        self.d['tmpfile'] = fetchall(cur)
        self.d['tags_cloud'] = self.get_tags(sort='desc')  # 添加文章所用到的按倒序排列的tags列表
        self.render('add.html', **self.d)

    def post(self):
        cur = self.db.cursor()

        title = self.get_argument('title', '')  # 标题
        content = self.get_argument('content', '')  # 内容
        render = html_body(content)  # 渲染rst结果到缓存
        posttime = datetime.now()
        tags = self.get_argument('tags', '').split(',')  # tag集合
        tags = tuple(set(tags))  # 去除重复记录
        files = self.get_argument('files', '').split(',')  # files集合
        if '' in files:
            files.remove('')#去掉空文件

        cur.execute('SELECT tag FROM tags WHERE tag in %s', (tags,))
        exists_tags = fetchall(cur)
        insert_tags = list(tags)
        for t in exists_tags:
            insert_tags.remove(t.tag)

        cur.execute('INSERT INTO articles(title,content,render,posttime) VALUES(%s,%s,%s,%s) RETURNING id',
            (title, content, render, posttime))#插入文章

        article_id = cur.fetchone()[0]#取得插入的文章id

        for t in insert_tags:#插入新的tag
            cur.execute('INSERT INTO tags VALUES(%s,%s)', (t, 0))

        for t in tags:
            cur.execute('INSERT INTO link_tags_articles(tag,article_id) VALUES(%s,%s)', (t, article_id))#插入tag关系

        cur.execute('UPDATE tags SET count = count+1 WHERE tag in %s', (tags,))#更新count值
        for f in files:
            cur.execute('INSERT INTO link_files_articles(filename,article_id) VALUES(%s,%s)', (f, article_id))#插入附件关系

        date_add(self.db, posttime)  # 添加日期计数
        #加到xapian全文索引中
        terms = title+content+(' '.join(tag for tag in tags))
        if type(terms) == unicode:
            terms = terms.encode('utf-8')
        search.index(article_id, terms, values={1:xapian.sortable_serialise(mktime(posttime.timetuple()))})
        search.flush()
        self.redirect(self.reverse_url('index'))


class DelHandler(AuthBlogHandler):
    """删除文章"""

    def get(self, id):
        id = int(id)  # 转换成数字
        cur = self.db.cursor()
        cur.execute('SELECT posttime FROM articles WHERE id = %s', (id,))
        posttime = fetchone(cur).posttime
        cur.execute('UPDATE tags SET count = count - 1 '
                    'WHERE tag in (SELECT tag FROM link_tags_articles WHERE article_id = %s)', (id,))
        cur.execute('DELETE FROM link_tags_articles WHERE article_id = %s', (id,))
        cur.execute('DELETE FROM tags WHERE count = 0')
        cur.execute('DELETE FROM link_files_articles  WHERE article_id = %s', (id,))
        cur.execute('DELETE FROM articles WHERE id = %s', (id,))#删除文章

        date_add(self.db, posttime, add=-1)  # 减去一个日期计数
        search.delete_document(id) # 删除索引
        search.flush()
        return self.write(u'ID:%s 的文章已删除' % id)


class ModifyHandler(AuthBlogHandler):
    """
    ....修改文章
    ...."""

    def get(self, id):
        id = int(id)
        cur = self.db.cursor()
        cur.execute('SELECT id, title, content, posttime, '
                    'ARRAY('
                    'SELECT tag FROM link_tags_articles WHERE link_tags_articles.article_id = articles.id'
                    ') as tags '
                    'FROM articles WHERE id = %s', (id,))
        self.d['article'] = fetchone(cur)
        cur.execute('SELECT filename FROM files '
                    'WHERE filename NOT IN (SELECT filename FROM link_files_articles)')
        self.d['tmpfile'] = fetchall(cur)
        self.d['tags_cloud'] = self.get_tags(sort='desc')  # 添加文章所用到的按倒序排列的tags列表
        self.render('modify.html', **self.d)

    def post(self, id):
        id = int(id)
        cur = self.db.cursor()
        title = self.get_argument('title', '')  # 标题
        content = self.get_argument('content', '')  # 内容
        render = html_body(content)  # 渲染rst结果到缓存
        tags = self.get_argument('tags', '').split(',')  # tag集合
        tags = tuple(set(tags))  # 去除重复记录
        files = self.get_argument('files', '').split(',')  # files集合
        if '' in files:
            files.remove('')#去掉空文件
        files = tuple(files)

        # ------------------处理tags---------------------
        if tags:
            cur.execute('SELECT tag FROM link_tags_articles WHERE article_id = %s and tag not in %s', (id, tags))
            del_tags = tuple([t.tag for t in fetchall(cur)])#要删除的tag
            cur.execute('SELECT tag FROM link_tags_articles WHERE article_id = %s and tag in %s', (id, tags))
            exists_tags = fetchall(cur)#已经存在的tag
            add_tags = list(tags)#要添加的tag

            for t in exists_tags:
                if t.tag.decode('utf-8') in add_tags:
                    add_tags.remove(t.tag.decode('utf-8'))#生成要添加的tag列表

            cur.execute('SELECT tag FROM tags WHERE tag in %s', (tags,))
            exists_tags = fetchall(cur)
            insert_tags = list(tags)#需要新插入的tag
            for t in exists_tags:
                if t.tag.decode('utf-8') in insert_tags:
                    insert_tags.remove(t.tag.decode('utf-8'))
        else:
            del_tags = ()
            add_tags = []
            insert_tags = []
            # ------------------处理附件---------------------
        if files:
            cur.execute('SELECT filename FROM link_files_articles WHERE article_id = %s and filename not in %s',
                (id, files))
            del_files = tuple([f.filename for f in fetchall(cur)])#要删除的file
            cur.execute('SELECT filename FROM link_files_articles WHERE article_id = %s and filename in %s',
                (id, files))
            exists_files = fetchall(cur)#已经存在的file
            add_files = list(files)#要添加的file

            for f in exists_files:
                if f.filename.decode('utf-8') in add_files:
                    add_files.remove(f.filename.decode('utf-8'))#生成要添加的file列表
        else:
            del_files = ()
            add_files = []

        if del_tags:
            cur.execute('DELETE FROM link_tags_articles WHERE tag in %s and article_id = %s', (del_tags, id))
            cur.execute('UPDATE tags SET count = count - 1 WHERE tag in %s', (del_tags,))
        cur.execute('DELETE FROM tags WHERE count <=0')
        for t in insert_tags:
            cur.execute('INSERT INTO tags VALUES(%s,%s)', (t, 0))

        for t in add_tags:
            cur.execute('INSERT INTO link_tags_articles(tag,article_id) VALUES(%s,%s)', (t, id))#给新tag添加关联

        if del_files:
            cur.execute('DELETE FROM link_files_articles WHERE filename in %s and article_id = %s', (del_files, id))
        for f in add_files:
            cur.execute('INSERT INTO link_files_articles(filename,article_id) VALUES(%s,%s)', (f, id))

        cur.execute('UPDATE articles SET title = %s,content=%s,render=%s WHERE id = %s',
            (title, content, render, id))#更新文章内容
        self.db.commit()

        #重新索引
        terms = title+content+(' '.join(tag for tag in tags))
        if type(terms) == unicode:
            terms = terms.encode('utf-8')
        search.update_index(id, terms)
        search.flush()
        return self.redirect(self.reverse_url('article', id))


class ArticleHandler(BlogHandler):
    '''文章显示'''

    def get(self, id):
        id = int(id)
        cur = self.db.cursor()
        cur.execute(
            'SELECT id,title,posttime,render,'
            'ARRAY('
            'SELECT tag FROM link_tags_articles WHERE link_tags_articles.article_id = articles.id'
            ') as tags '
            'FROM articles WHERE id = %s'
            , (id,))
        self.d['article'] = fetchone(cur)
        if not self.d['article']:
            return self.send_error(status_code=404)
        self.render('article.html', **self.d)


class FeedsHandler(BlogHandler):
    '''RSS订阅'''

    def get(self):
        self.set_header('Content-Type', 'application/xml')
        if os.path.exists('feeds.xml') and time()\
                                           - os.path.getmtime('feeds.xml') < 1800:
            self.write(open('feeds.xml', 'rb').read())
        else:
            FeedsHandler.build(self)
            self.write(open('feeds.xml', 'rb').read())

    @staticmethod
    def build(self):
        cur = self.db.cursor()
        cur.execute('SELECT id, title, posttime, render, '
                    'ARRAY('
                    'SELECT tag FROM link_tags_articles WHERE link_tags_articles.article_id = articles.id'
                    ') as tags '
                    'FROM articles WHERE id != 0 '
                    'ORDER BY posttime desc LIMIT 30')
        articles = fetchall(cur)
        rss = PyRSS2Gen.RSS2(title='Chronos',
            link='http://blog.plotcup.com',
            description='',
            items=[PyRSS2Gen.RSSItem(title=a['title'].decode('utf-8'),
                link='http://blog.plotcup.com'
                + self.reverse_url('article', a['id']),
                description=a['render'].decode('utf-8'),
                guid=PyRSS2Gen.Guid(self.reverse_url('article'
                    , a['id'])), pubDate=a['posttime'])
                   for a in articles])
        rss.write_xml(open('feeds.xml', 'wb'))


class UploadFileHandler(BlogHandler):
    '''
    下载上传的文件类
    nginx里面的配置:
    location /static/upload/{
        proxy_pass http://127.0.0.1:8000/upload/;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header REMOTE_ADDR $remote_addr;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Accept-Encoding '';
        proxy_set_header Host $host;
        client_max_body_size 50m;
        client_body_buffer_size 256k;
    }

    location /uploadfiles/{
        internal;#内容指令
        alias /root/production/app/pitaya/static/upload/;
        expires 1d;
    }
    '''

    def get(self, filename):
        mimetype = mimetypes.guess_type(filename)[0]
        if not mimetype:
            mimetype = 'application/octet-stream'
        self.set_header('Content-Type', mimetype)
        cur = self.db.cursor()
        cur.execute('SELECT filestore FROM files WHERE filename = %s', (filename,))
        filestore = fetchone(cur)
        if filestore:
            self.set_header('X-Accel-Redirect', os.path.join('/uploadfiles', filestore.filestore))
        else:
            self.set_status(404)
