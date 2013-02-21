#-*- encoding:utf-8 -*-

from utils.requesthandler import AuthBlogHandler
from utils.func import json, prefix_rand, fetchall, fetchone
from urllib import unquote
from hashlib import md5
import os

class UploaderHandler(AuthBlogHandler):
    """
    上传文件
    """

    def post(self):
        filename = unquote(self.request.query[7:])
        if filename == "":
            return self.write(json.dump({"error": u"文件名错误"}))

        prefix = prefix_rand()
        cur = self.db.cursor()
        for i in range(6):
            cur.execute('SELECT count(0) as count FROM files WHERE filename = %s', ('%s/%s' % (prefix, filename),))
            if fetchone(cur).count > 0:
                prefix = prefix_rand()
                if i >= 5:
                    return self.write(json.dump({"error": u"文件名重复次数过多"}))
            else:
                break
        md5text = md5(self.request.body).hexdigest()#计算文件md5值
        try:
            open('static/upload/%s' % md5text, 'wb').write(self.request.body)#保存到文件系统中。
            cur.execute('INSERT INTO files(filename,filestore) VALUES(%s,%s)', ('%s/%s' % (prefix, filename), md5text))
        except Exception, e:
            try:
                cur.execute('DELETE FROM files WHERE filestore=%s', (md5text,))#从数据库中删除错误的记录
                os.unlink('static/upload/%s' % md5text)#从文件系统中删除错误的文件
            except:
                self.db.rollback()

            return self.write(json.dump({'error': u'数据存取错误'}))

        self.db.commit()
        d = {}
        d['success'] = 'ok'
        d['prefix'] = prefix
        d['filename'] = filename
        return self.write(json.dump(d))


class DelfileHandler(AuthBlogHandler):
    """
    删除临时文件
    """

    def get(self, key):
        key = unquote(key)
        cur = self.db.cursor()
        try:
            cur.execute('SELECT * FROM files WHERE filename = %s', (key,))
            f = fetchone(cur)
            try:
                os.unlink('static/upload/%s' % f.filestore)
            except:
                pass
            cur.execute('DELETE FROM files WHERE filename = %s', (key,))
            self.db.commit()
        except Exception, e:
            print e
        return self.write('OK')
        
