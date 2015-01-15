#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'David Lin'

'''
Database operation module. This module is independent with web module.
'''

import time, logging

import db # import the file we write named db

class Field(object): # Database entity instance Field

	_count = 0

	def __init__(self, **kw):
		self.name = kw.get('name',None)
		self._default = kw.get('default',None)
		self.primary_key = kw.get('primary_key', False)
		self.nullable = kw.get('nullable',False) # allow null
		self.updatable = kw.get('updatable', True)
		self.insertable = kw.get('insertable', True) # Field insertable
		self.ddl = kw.get('ddl','')
		self.order = Field._count    # _count for order
		Field._count = Field._count + 1

	@property
	def default(self):
		d = self._default
		return d() if callable(d) else d

	def __str__(self):
		s = ['<%s:%s,%s,default(%s),' % (self.__class__.__name__, self.name, self.ddl, self._default)]
		self.nullable and s.append('N')
		self.updatable and s.append('U') # if self.updatable then s.append('U')
		self.insertable and s.append('I')
		s.append('>')
		return ''.join(s)

class StringField(Field):

	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = '' # default values for this Field
		if not 'ddl' in kw:
			kw['ddl'] = 'varchar(255)'
		super(StringField, self).__init__(**kw)

class IntegerField(Field):

	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = 0
		if not 'ddl' in kw:
			kw['ddl'] = 'bigint' # data type
		super(IntegerField, self).__init__(**kw)

class BooleanField(Field):

	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = False
		if not 'ddl' in kw:
			kw['ddl'] = 'bool'
		super(BooleanField, self).__init(**kw)

class FloatField(Field):

	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = 0.0
		if not 'ddl' in kw:
			kw['ddl'] = 'real'
		super(BooleanField, self).__init(**kw)

class TextField(Field):

	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = ''
		if not 'ddl' in kw:
			kw['ddl'] = 'text'
		super(BooleanField, self).__init(**kw)

class BlobField(Field):

	def __init__(self, **kw):
		if not 'default' in kw:
			kw['default'] = ''
		if not 'ddl' in kw:
			kw['ddl'] = 'blob'
		super(BlobField, self).__init__(**kw)

class VersionField(Field):

	def __init__(self, name=None): # why so special ?
		super(VersionField, self).__init__(name=name, default=0, ddl='bigint')

_triggers = frozenset(['pre_insert','pre_update','pre_delete'])  # three trigger

def _gen_sql(table_name, mappings):
	pass

class ModelMetaclass(type):
	'''
	Metaclass for model objects, type replace object.
	'''
	# Example:
	'''
	class User(Model):
		id = IntegerField('id')
		name = StringField('username')
		email = StringField('email')
		password = StringField('password')

	# 创建一个实例：
	u = User(id=12345, name='Michael', email='test@orm.org', password='my-pwd')
	# 保存到数据库：
	u.save()
	'''
	def __new__(cls, name, bases, attrs):
		# cls : class instance 
		# name : subclass name
		# bases: superclass collections
		# attrs: method or attribute of class instance

		#skip base Model class:
		if name=='Model': 
			return type.__new__(cls, name, bases, attrs)

		# subclass which extends Model
		# store all subclasses info: still don't get it
		if not hasattr(cls, 'subclasses'): # hold subclasses 
			cls.subclasses = {}
		if not name in cls.subclasses:
			cls.subclasses[name] = name
		else:
			logging.warning('Redefine class: %s' % name)

		logging.info('Scan ORMapping %s...' % name)
		mappings = dict()
		primary_key = None
		for k, v in attrs.iteritems():
			if isinstance(v, Field):
				if not v.name:
					v.name = k   # such as name = StringField('') --> now v.name = name
				logging.info('Found mapping: %s => %s' %(k,v))
				# check duplicate primary key:
				if v.primary_key:
					if primary_key:
						raise TypeError('Cannot define more than 1 primary key in class: %s' % name)
					if v.updatable:
						logging.warning('NOTE: change primary key to non-updatable. ')
						v.updatable = False
					if v.nullable:
						logging.warning('Note: change primary key to non-nullable.')
						v.nullable = False
					primary_key = v  # name  = StringField('username')  v = StringField('username')
				mappings[k] = v   # mapping k --> name v StringField('username')
		# check exist of primary key:
		if not primary_key:
			raise TypeError('Primary key not defined in class: %s' % name)
		for k in mappings.iterkeys():
			attrs.pop(k)  # k --> name delete StringField('username') from attrs
		if not '__table__' in attrs:
			attrs['__table__'] = name.lower() # __table__ is class name
		attrs['__mappings__'] = mappings  # replace with attributes Mappings
		attrs['__primary_key__'] = primary_key
		attrs['__sql__'] = lambda self: _gen_sql(attrs['__table__'], mappings)
		for trigger in _triggers:
			if not trigger in attrs:
				attrs[trigger] = None # add trigger to attrs
		return type.__new__(cls, name, bases, attrs)		

class Model(dict):
	__metaclass__ = ModelMetaclass

	def __init__(self, **kw):
		super(Model, self).__init__(**kw) # the **kw survive as a data access between user and database

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

	@classmethod
	def get(cls, pk):
		'''
		Get by primary key.
		'''
		d = db.select_one('select * from %s where %s=?' % (cls.__table__, cls.__primary_key__.name),pk)
		return cls(**d) if d else None # return itself d can be list or dict , I think it is dict

	@classmethod
	def find_first(cls, where, *args):
		'''
		Find by where clause
		'''
		d = db.select_one('select * from %s %s' % (cls.__table__, where), *args)
		return cls(**d) if d else None

	@classmethod
	def find_all(cls, *args):
		'''
		Find all and return list.
		'''
		L = db.select('select * from `%s`' % cls.__table__)
		return [cls(**d) for d in L]

	@classmethod
	def count_all(cls):
		return db.select_int('select count(`%s`) from `%s`' % (cls.__primary_key__.name, cls.__table__))

	@classmethod
	def count_by(cls, where, *args):
		'''
		select count(pk) from table where ...
		'''
		return db.select_int('select count(`%s`) from `%s` %s' % (cls.__primary_key__.name, cls.__table__, where), *args)

	def update(self):
		self.pre_update and self.pre_update() # pre_update and pre_update() are trigger
		L = []
		args = []
		for k,v in self.__mappings__.iteritems():
			if v.updatable:
				arg = getattr(self, k)
			else:
				arg = v.default
				setattr(self, k, arg)
			L.append('`%s`=?' % k)
			args.append(arg)
		pk = self.__primary_key__.name
		args.append(getattr(self,pk))
		db.update('update `%s` set %s where %s=?' % (self.__table__, ','.join(L), pk), *args)
		return self
		
	def delete(self):
		self.pre_delete and self.pre_delete()
		pk = self.__primary_key__.name
		args = (getattr(self, pk), )
		db.update('delete from `%s` where `%s`=?' % (self.__table__, pk), *args)
		return self

	def insert(self):
		self.pre_insert and self.pre_insert()
		params = {}
		for k,v in self.__mappings__.iteritems():
			if v.insertable:
				if not hasattr(self, k):
					setattr(self, k, v.default)
				params[v.name] = getattr(self, k)
		db.insert('%s' % self.__table__, **params)
		return self
		
if __name__=='__main__':
	logging.basicConfig(level=logging.DEBUG)
	db.create_engine('root','Linux818','test')
	db.update('drop table if exists user')
	db.update('create table user (id int primary key, name text, email text, passwd text, last_modified real)')
	import doctest
	doctest.testmod()	
