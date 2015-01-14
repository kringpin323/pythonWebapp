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

class DBError(Exception):
	pass

class MultiColumnsError(DBError): # extends from DBError means it is an error from DB
	pass


class _LasyConnection(object):

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
		self.transactions = 0 # transactions for commit

	def is_init(self):
		return not self.connection is None

	def init(self):
		logging.info('open lazy connection')
		self.connection = _LasyConnection()
		self.transactions = 0 # I don't understand

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
	defaults = dict(use_unicode=True, charset=u'utf8',collation = 'utf8_general_ci',autocommit=False)
	for k,v in defaults.iteritems():
		params[k] = kw.pop(k,v)
	params.update(kw)
	params['buffered'] = True
	engine = _Engine(lambda:mysql.connector.connect(**params))
	# test connection...
	logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))

class _ConnectionCtx(object):
	'''
	_ConnectionCtx object that can open and close connection context. _ConnectionCtx object can be nested and
	only the most outer connection has effect.

	with connection():
		pass 
		with connection():
			pass
	'''
	def __enter__(self):
		global _db_ctx
		self.should_cleanup = False
		if not _db_ctx.is_init():
			_db_ctx.init()
			self.should_cleanup = True
		return self

	def __exit__(self , exctype, excvalue, traceback):
		global _db_ctx
		if self.should_cleanup:
			_db_ctx.cleanup() # mySql cleanup

def with_connection(func):
	'''
	Decorator for reuse connection.

	@with_connection
	def foo(*args, **kw):
		f1()
		f2()
		f3()
	'''
	@functools.wraps(func)
	def _wrapper(*args, **kw):
		with _ConnectionCtx():
			return func(*args, **kw)
	return _wrapper

@with_connection
def _update(sql, *args):
	global _db_ctx
	cursor = None
	sql = sql.replace('?', '%s') # replace ? with %s in sql
	logging.info('SQL: %s, ARGS: %s' % (sql,args)) # you can see what sql right now in here
	try:
		cursor = _db_ctx.connection.cursor() # what it have done is to detach "SQL Injection Attack"
		cursor.execute(sql, args) # execute it 
		r = cursor.rowcount # we use cursor to execute and get answer
		if _db_ctx.transactions ==0: # question is , what situation transactions is not Zero
			# no transaction enviroment:
			logging.info('auto commit')
			_db_ctx.connection.commit()
		return r
	finally:
		if cursor:
			cursor.close()

def _select(sql, first, *args):
	'execute select SQL and return unique result or list results.'
	global _db_ctx
	cursor = None
	sql = sql.replace('?', '%s') # protect from SQL Injection Attack
	logging.info('SQL: %s, ARGS: %s' % (sql, args)) 
	try:
		cursor = _db_ctx.connection.cursor()
		cursor.execute(sql, args) # sentences execute can dull with all kind of sql 
		if cursor.description:
			names = [x[0] for x in cursor.description]
		if first: # means : return First Find or not
			values = cursor.fetchone()  # means fetch one 
			if not values:
				return None
			return Dict(names, values)
		return [Dict(names,x) for x in cursor.fetchall()]  # # a list builded of lots of Dict instance 
	finally:
		if cursor:
			cursor.close()

@with_connection
def select_one(sql , *args):
	'''
	Execute select SQL and expected one result.
	if no , return None
	If more than one, the first one returned.

	>>> u1 = dict(id=100 , name='David', email='kringpin_lin@163.com' , passwd='Linux818' , last_modified=time.time())
	>>> u2 = dict(id=101 , name='John', email='1325742149@qq.com' , passwd='Linux818' , last_modified=time.time())
	>>> insert('user', **u1)
	1
	>>> insert('user', **u2)
	1
	>>> u = select_one('select * from user where id=?', 100)
	>>> u.name
	u'David'
	'''
	return _select(sql, True, *args)

@with_connection
def select_int(sql, *args):
	'''
	Execute select SQL and expected one int and only one int result

	>>> n = update('delete from user')
	>>> u1 = dict(id=10086, name='Ada', email='kringpin323@gmail.com', passwd = 'Linux818', last_modified = time.time())
	>>> u2 = dict(id=10087, name='Adam', email='adam@test.org', passwd = 'Linux818', last_modified=time.time())
	>>> insert('user', **u1)
	1
	>>> insert('user', **u2)
	1
	>>> select_int('select name from user where email=?','adam@test.org')
	u'Adam'
	>>> select_int('select id from user where email=?','adam@test.org')
	10087
	>>> select_int('select count(*) from user')
	2
	>>> select_int('select count(*) from user where email=?','kringpin323@gmail.com')
	1
    >>> select_int('select id , name from user where email=?','adam@test.org')
    Traceback (most recent call last):
    	...
    MultiColumnsError: Expect only one column.
	'''
	d = _select(sql, True, *args) # a list builded of lots of Dict instances  or an Dict instance 
	if len(d)!=1: # so easy to define an Error , if it is an Dict instance , len(d)==(int) # help(len)  Return the number of items of a sequence or mapping
		raise MultiColumnsError('Expect only one column.')
	return d.values()[0]

@with_connection
def select(sql, *args):
	'''
	Execute select SQL and return list or empty list if no result.

	>>> u1 = dict(id=200, name='Wall.E', email='wall.e@test.org', passwd='back-to-earth', last_modified=time.time())
	>>> u2 = dict(id=201, name='Eva', email='eva@test.org', passwd='back-to-earth', last_modified=time.time())
	>>> insert('user', **u1)
	1
	>>> insert('user', **u2)
	1
	>>> L = select('select * from user where id=?' ,9090909)
	>>> L
	[]
	>>> L = select('select * from user where id=?', 200)
	>>> L[0].email
	u'wall.e@test.org'
	>>> L = select('select * from user where passwd=? order by id desc', 'back-to-earth')
	>>> L[0].name
	u'Eva'
	>>> L[1].name
	u'Wall.E'
	'''
	return _select(sql, False, *args)

def insert(table, **kw):
	'''
	Execute insert SQL.

	>>> u1 = dict(id=2000, name='Bob', email='bob@test.org', passwd='Linux818',last_modified=time.time())
	>>> insert('user',**u1)
	1
	'''
	cols, args = zip(*kw.iteritems())
	sql = 'insert into `%s` (%s) values (%s)' % (table, ','.join(['`%s`' % col for col in cols]), ','.join(['?' for i in range(len(cols))])) # bulid sql with key not values
	return _update(sql, *args)

def update(sql , *args):
	r'''
	Execute update SQL.

	>>> u1 = dict(id=1000, name='David', email='kringpin_lin@163.com', passwd='Linux818',last_modified=time.time())
	>>> update('update user set passwd=? where id=?', '***', '123\' or id=\'456')
	0
	'''
	return _update(sql, *args)

if __name__=='__main__':
	logging.basicConfig(level=logging.DEBUG)
	create_engine('root','Linux818','test')

	update('drop table if exists user')
	update('create table user (id int primary key, name text, email text, passwd text, last_modified real)')

	import doctest
	doctest.testmod()

