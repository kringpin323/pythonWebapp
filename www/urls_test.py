#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'David Lin'

import logging

from transwarp.web import get, view # from web module import get and view decorator

from models import User, Blog, Comment

# @view('test_users.html')
# @get('/')
# def test_users():
# 	users = User.find_all()
# 	return dict(users=users)

@view('blogs.html')
@get('/')
def index():
	blogs = Blog.find_all()
	# check log user:
	user = User.find_first('where email=?','admin@example.com')
	return dict(blogs=blogs, user=user)
	