#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'David Lin'

'''
A WSGI application entry.
An file to run WSGI application , an entry
'''

import logging; logging.basicConfig(level=logging.INFO)

import os, time
from datetime import datetime

from transwarp import db
from transwarp.web import WSGIApplication, Jinja2TemplateEngine

from config import configs

def datetime_filter(t):
	delta = int(time.time() - t)
	if delta < 60:
		return u'one minutes'
	if delta < 3600:
		return u'%s分钟前' % (delta // 60)
	if delta < 86400:
		return u'%s小时前' % (delta // 3600)
	if delta < 604800:
		return u'%s天前' % (delta // 86400)
	dt = datetime.fromtimestamp(t)
	return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

# init db:
db.create_engine(**configs.db)

# init wsgi app:
wsgi = WSGIApplication(os.path.dirname(os.path.abspath(__file__)))

# init template engine
template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates'))
template_engine.add_filter('datetime', datetime_filter)

wsgi.template_engine = template_engine

import urls_test

wsgi.add_module(urls_test)

if __name__ == '__main__':
	wsgi.run(9004, host='0.0.0.0') # you can visit it outside
else:
	application =wsgi.get_wsgi_application()

