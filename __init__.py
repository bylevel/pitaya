#-*- encoding:utf-8 -*-

from tornado import ioloop, web, wsgi
from utils import urls, settings

def buildapp(iswsgi=False):
	if iswsgi:
		return wsgi.WSGIApplication(
				urls,
				**settings
			)
	else:
		return web.Application(
				urls,
				**settings
			)

if __name__ == '__main__':
	application = buildapp()
	application.listen(8000)
	ioloop.IOLoop.instance().start()#运行tornado web server
