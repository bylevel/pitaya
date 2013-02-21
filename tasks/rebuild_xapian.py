#!/usr/bin/env python
# encoding: utf-8

from utils.func import search, fetchall
from utils.requesthandler import db
import xapian, time

def call():
    """运行此任务
    :returns: none

    """
    cur = db.cursor()
    cur.execute(
        'SELECT id, title, content, posttime, '
        'ARRAY('
        'SELECT tag FROM link_tags_articles WHERE link_tags_articles.article_id = articles.id'
        ') as tags '
        'FROM articles WHERE id != %s ',
        (0,))

    for row in fetchall(cur):
        search.index(row['id'], row['title']+row['content']+(' '.join(tag for tag in row['tags'])), values={1:xapian.sortable_serialise(time.mktime(row['posttime'].timetuple()))})

    search.flush()
