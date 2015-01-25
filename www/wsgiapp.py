#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'David Lin'

'''
A WSGI application entry.
An file to run WSGI application , an entry
'''

import logging; logging.basicConfig(level=logging.INFO)

import os

from transwarp import db
from transwarp.web import WSGIApplication, Jinja2TemplateEngine

from config import configs

# init db:
db.create_engine(**configs.db)

# init wsgi app:
wsgi = WSGIApplication(os.path.dirname(os.path.abspath(__file__)))

# init template engine
template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates'))

wsgi.template_engine = template_engine

import urls_test

wsgi.add_module(urls_test)

if __name__ == '__main__':
	wsgi.run(9003) # Ip: 127.0.0.1, Port: 9001

