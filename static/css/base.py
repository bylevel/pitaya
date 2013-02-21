__author__ = 'chronos'

from subprocess import Popen

base_css = open('base.css', 'wb')
Popen(['scss', '-C', '-t', 'compressed', '-E', 'utf-8', 'base.scss'], stdout=base_css, shell=True).communicate()