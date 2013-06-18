#-*- encoding:utf-8 -*-

import json as json_old
from StringIO import StringIO
from random import sample
import smtplib, mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Header import Header
from datetime import datetime

class json():
    @staticmethod
    def dump(obj):
        """
        将dict转换成json
        """
        tmpfp = StringIO()
        json_old.dump(obj, tmpfp)
        tmpfp.seek(0)
        return tmpfp.read()

    @staticmethod
    def load(obj):
        """
        将json转换成dict
        """
        tmpfp = StringIO()
        tmpfp.write(obj)
        tmpfp.seek(0)
        return json_old.load(tmpfp)


class DataItem(dict):
    '''
    单条数据项
    '''

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


class Fetchone(DataItem):
    '''
    从cursor获取一条记录并转换数据调用方式
    '''

    def __init__(self, description, rs):
        for i in range(len(description)):
            self.__setattr__(description[i].name, rs[i])


def fetchone(cur):
    rs = cur.fetchone()
    if rs:
        return Fetchone(cur.description, rs)
    else:
        return None


class Fetchall():
    '''
    从cursor中获取一批记录并转换数据调用方式
    '''

    def __init__(self, description, rs):
        tmprs = []
        for r in rs:
            tmp = DataItem()
            for i in range(len(description)):
                tmp[description[i].name] = r[i]
            tmprs.append(tmp)
        self.rs = tmprs
        self.i = -1

    def __iter__(self):
        return self

    def next(self):
        self.i += 1
        try:
            return self.rs[self.i]
        except:
            raise StopIteration

    def __str__(self):
        return [r for r in self.rs]


def fetchall(cur):
    rs = cur.fetchall()
    if rs:
        return Fetchall(cur.description, rs)
    else:
        return []


def prefix_rand():
    randstr = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM-_1234567890"
    rs = ""
    for i in range(6):
        rs += sample(randstr, 1)[0]

    return rs


def Pagination(d, page, pagesize, totalrows):
    '''
    生成分页信息
    @param d:传的页面d值
    @param page:当前页面
    @param pagesize:分页大小
    @param totalrows:总记录数
    '''
    d['totalrows'] = totalrows
    d['page'] = page
    d['totalpage'] = totalrows / pagesize
    if totalrows % pagesize > 0:
        d['totalpage'] += 1
    pages = []
    for i in range(-3, 0):
        if page + i > 0:
            pages.append(page + i)
    pages.append(page)
    for i in range(1, 10):
        if page + i <= d['totalpage']:
            pages.append(page + i)
    d['pages'] = pages
    return d


def date_add(db, date, add=1):
    '''
    添加日期计数到数据库
    '''
    cur = db.cursor()
    cur.execute('SELECT month FROM dates WHERE month = %s', (date.strftime('%Y年%m月'),))
    if cur.fetchone():
        cur.execute('UPDATE dates SET count = count+%s WHERE month = %s', (add, date.strftime('%Y年%m月')))
    else:
        cur.execute('INSERT INTO dates VALUES(%s,%s)', (date.strftime('%Y年%m月'), add))

    cur.execute('DELETE FROM dates WHERE count <= 0')#删除统计数小于等于零的记录
    db.commit()


def StripHtml(html):
    """转化html标记"""
    html = html.replace('<', '&lt;')
    html = html.replace('>', '&gt;')
    html = html.replace('"', '&quot;')
    html = html.replace(' ', '&nbsp;')
    html = html.replace('\r\n', '<br>')
    return html


def send_email( _to, _subject, _msg):
    '''发送邮件'''
    try:
        msg = MIMEMultipart()
        msg['From'] = "xielong2@qq.com"
        msg['To'] = _to
        msg['Subject'] = Header(_subject, charset='UTF-8')#中文主题

        #添加邮件内容
        txt = MIMEText(_msg, _subtype='html', _charset='UTF-8')
        msg.attach(txt)

        #发送邮件
        smtp = smtplib.SMTP()
        smtp.connect('smtp.163.com:25')
        smtp.login('xielong1024', '0487561')
        smtp.sendmail('xielong1024@163.com', _to, msg.as_string())
        smtp.quit()
        return True
    except Exception, e:
        print datetime.now()
        print e
        return False

import xapian, config
from mmseg.search import seg_txt_2_dict

class Xapian():
    """xapian search class """

    def __init__(self):
        """init xapian search class
        :returns: class

        """
        self.db = xapian.WritableDatabase(config.xapian_index_dir, xapian.DB_CREATE_OR_OPEN)
        self.enquire = xapian.Enquire(self.db)
        self.enquire.set_sort_by_value(1, True)

    def get_document(self, id):
        """获取doc

        :id: id
        :returns: Document

        """
        return self.db.get_document(id)

    def delete_document(self,id):
        """删除索引

        :id: 索引id
        """
        try:
            return self.db.delete_document(id)
        except:
            return None

    def update_index(self, id, text=None, values=None, data=None):
        """更新索引

        :id: 要替换的id
        :doc: 新的doc
        """
        try:
            doc = self.get_document(id)
        except:
            return False

        if text:
            doc.clear_terms()#清除terms
            for word, value in seg_txt_2_dict(text).iteritems():
                doc.add_term(word)

        if values:
            doc.clear_values()
            for key, value in values.iteritems():
                doc.add_value(key, value)

        if data:
            doc.set_data(data)

        try:
            self.db.replace_document(id, doc)
            return True
        except:
            return False

    def index(self, id, text, values={}, data=''):
        """index to xapian

        :id: data id
        :text: search content is utf-8
        :returns: boolean

        """
        doc = xapian.Document()
        for word, value in seg_txt_2_dict(text).iteritems():
            print word, value
            doc.add_term(word)

        #添加value用于排序，key似乎只能是数字
        for key, value in values.iteritems():
            doc.add_value(key, value)

        if data:
            doc.set_data(data)

        try:
            self.db.replace_document(id, doc)
            return True
        except:
            return False

    def search(self, keywords, offset=0, limit=10):
        """search xapian

        :keywords: 搜索的关键字
        :offset: 起始位置
        :limit: 结束位置
        :returns: matches对象

        """
        query_list = []
        for word, value in seg_txt_2_dict(keywords.encode('utf-8')).iteritems():
            query = xapian.Query(word)
            query_list.append(query)

        if len(query_list) != 1:
            query = xapian.Query(xapian.Query.OP_AND, query_list)
        else:
            query = query_list[0]

        self.enquire.set_query(query)
        matches = self.enquire.get_mset(offset, limit, 10000)
        return matches

    def flush(self):
        """flush to disk
        :returns: flush结果

        """
        return self.db.flush()

search = Xapian()

