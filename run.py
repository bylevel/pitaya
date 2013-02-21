#!/usr/bin/env python
#-*- encoding:utf-8 -*-

from optparse import OptionParser

from __init__ import buildapp, ioloop

def getparser():
	'''解析命令行参数'''
	parser = OptionParser()
	parser.add_option('-H', '--host', dest='host', default='0.0.0.0',\
		help=u'设置监听的ip，默认为0.0.0.0', metavar='host')
	parser.add_option('-p', '--port', dest='port', type='int', default='8000',\
		help=u'设置监听的端口,默认为8000', metavar='port')
	options, args = parser.parse_args()
	return options, args

if __name__ == '__main__':
	options = getparser()[0]
	print 'pitaya listen %s:%s'%(options.host, options.port)
	buildapp().listen(options.port, address=options.host)
	ioloop.IOLoop.instance().start()#运行tornado web server
else:
	application = buildapp(iswsgi=True)
