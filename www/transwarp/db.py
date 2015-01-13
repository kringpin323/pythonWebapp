#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'David Lin'

'''
Database operation module. Learn from project of Michael Liao
'''

import time, uuid, functools, threading, logging

# Dict object:

class Dict(dict):
	'''
	Simple dict but support access as x.y style

	>>> d1 = Dict()
	>>> d1['x'] = 100
	>>> d1.x
	100
	>>> d1.y = 200
	>>> d1['y']
	200
	>>> d2 = Dict(a=1, b=2, c='3')
	>>> d2.c
	'3'
	>>> d2['empty']
	Traceback (most recent call last):
		...
	KeyError: 'empty'
	>>> d2.empty
	Traceback (most recent call last):
		...
	AttributeError: 'Dict' object has no attribute 'empty'
	>>> d3 = Dict(('a','b','c'), (1,2,3))
	>>> d3.a
	1
	>>> d3.b
	2
	>>> d3.c
	3
	'''

	def __init__(self, names=(), values=(),**kw):
		super(Dict, self).__init__(**kw)
		for k,v in zip(names, values):
			self[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key , value):
		self[key] = value

class _LazyConnection(object):

	def __init__(self):
		self.connection = None # the connection to MySql using to return 

	def cursor(self):
		if self.connection is None:
			connection = engine.connect()
			logging.info('open connection <%s>...' % hex(id(connection)))
			self.connection = connection
		return self.connection.cursor()

	def rollback(self):
		self.connection.rollback() # MySQL rollback

	def commit(self):
		self.connection.commit()

	def cleanup(self):
		if self.connection: # a good custom. To check before to use
			connection = self.connection # watch size they live
			self.connection = None
			logging.info('close connection <%s>...' % hex(id(connection)))
			connection.close()

class _DbCtx(threading.local):
	'''
	Thread local object that holds connection infomation . 
	'''
	def __init__(self):
		self.connection = None # connection to MySql 
		self.transaction = 0 # transaction for commit

	def is_init(self):
		return not self.connection is None

	def init(self):
		logging.info('open lazy connection')
		self.connection = _LasyConnection()
		self.transaction = 0 # I don't understand

	def cleanup(self):
		self.connection.cleanup() # using MySql function to cleanup
		self.connection = None # manual cleanup

	def cursor(self):
		'''
		Return MySql cursor
		'''
		return self.connection.cursor()


# thread-local db context:
_db_ctx = _DbCtx()

# global engine object:
engine = None

class _Engine(object):

	def __init__(self, connect):
		self._connect = connect # function pointer for connection of MySQL

	def connect(self):
		return self._connect()

def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw): # kw for ...
	'''
	create an engine connecting MySQL
	'''
	import mysql.connector
	global engine
	if engine is not None:
		raise DBError('Engine is already initialized.')
	params = dict(user=user, password= password, database= database, host = host ,port = port)
	defaults = dict(use_unicode=True, charset='utf-8',collation = 'utf_general_ci',autocommit=False)
	for k,v in defaults.iteritems():
		params[k] = kw.pop(k,v)
	params.update(kw)
	params['buffered'] = True
	engine = _Engine(lambda:mysql.connector.connect(**parms))
	# test connection...
	logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))

def insert(table, **kw):
	pass

def update(sql , *args):
	r'''
	Execute update SQL.

	>>> u1 = dict(id=1000, name='David', email='kringpin_lin@163.com', passwd='Linux818',last_modified=time.time())
	>>> insert('user', **u1)
	1

	'''
	pass

if __name__=='__main__':
	logging.basicConfig(level=logging.DEBUG)
	create_engine('DavidPythonWebapp','Linux818','DavidPersonalWebsite')

	update('drop table if exists user')
	update('create table user (id int primay key, name text, email text, passwd text, last_modified real')

	import doctest
	doctest.testmod()