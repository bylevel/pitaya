#!/usr/bin/env python
#-*- encoding:utf-8 -*-

from utils.func import search
import sys

exec('from tasks import %s as run'%sys.argv[1])

run.call()
