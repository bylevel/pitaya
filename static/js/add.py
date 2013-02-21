#coding:utf-8
__author__ = 'chronos'

from subprocess import Popen, PIPE

add_coffee = open('add.coffee', 'rb')
add_coffee = Popen(['coffee', '-cb', '-s'], stdin=add_coffee, stdout=PIPE, shell=True)
add_coffee = add_coffee.communicate()[0]

fileuploader_js = open('fileuploader.js', 'rb').read()
codemirror_js = open('codemirror/lib/codemirror.js', 'rb').read()
rst_js = open('codemirror/mode/rst/rst.js', 'rb').read()

join_js = '\r\n'.join([fileuploader_js, codemirror_js, rst_js, add_coffee])#合并两个js

add_js = open('add.js', 'wb')
out = Popen(['uglifyjs', '-nc'], stdin=PIPE, stdout=add_js, shell=True)
out.stdin.write(join_js)
out.communicate()