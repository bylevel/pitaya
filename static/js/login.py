#coding:utf-8
__author__ = 'chronos'

from subprocess import Popen, PIPE

login_coffee = open('login.coffee', 'rb')
login_coffee = Popen(['coffee', '-cb', '-s'], stdin=login_coffee, stdout=PIPE, shell=True)

login_js = open('login.js', 'wb')
out = Popen(['uglifyjs', '-nc'], stdin=login_coffee.stdout, stdout=login_js, shell=True)
out.communicate()