#coding:utf-8
__author__ = 'chronos'

from subprocess import Popen, PIPE

base_coffee = open('base.coffee', 'rb')
base_coffee = Popen(['coffee', '-cb', '-s'], stdin=base_coffee, stdout=PIPE, shell=True)
base_coffee = base_coffee.communicate()[0]

jquery_cookie_js = open('jquery.cookie.js', 'rb').read()

join_js = '\r\n'.join([jquery_cookie_js, base_coffee])#合并两个js

base_js = open('base.js', 'wb')
out = Popen(['uglifyjs', '-nc'], stdin=PIPE, stdout=base_js, shell=True)
out.stdin.write(join_js)
out.communicate()