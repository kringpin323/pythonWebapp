#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'David Lin'

import logging

from transwarp.web import get, view # from web module import get and view decorator

from models import User, Blog, Comment

@view('test_users.html')
@get('/')
def test_users():
	users = User.find_all()
	return dict(users=users)
	