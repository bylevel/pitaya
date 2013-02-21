__author__ = 'chronos'

from subprocess import Popen

add_css = open('add.css', 'wb')
Popen(['scss', '-C', '-t', 'compressed', '-E', 'utf-8', 'add.scss'], stdout=add_css, shell=True).communicate()