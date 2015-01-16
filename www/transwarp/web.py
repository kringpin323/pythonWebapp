#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A simple, lightweight, WSGI-compatible web framework.
'''

__author__ = 'David Lin'

import types, os, re, cgi, sys, time, datetime, functools, mimetypes, threading, logging, urllib, traceback

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

# thread local object for storing request and response:

ctx = threading.local()

# Dict object

class Dict(dict):
	'''
	Simple dict but support access as x.y style.

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
	>>> d3 = Dict(('a', 'b', 'c'), (1, 2, 3))
	>>> d3.a
	1
	>>> d3.b
	2
	>>> d3.c
	3
	'''
	def __init__(self, names=(), values=(), **kw):
		super(Dict,self).__init__(**kw)
		for k, v in zip(names, values):
			self[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

_TIMEDELTA_ZERO = datetime.timedelta(0)

# timezone as UTC+8:00, UTC-10:00

_RE_TZ = re.compile('^([\+\-])([0-9]{1,2})\:([0-9]{1,2})$')

class UTC(datetime.tzinfo):
	'''
	A UTC tzinfo object.

	>>> tz0 = UTC('+00:00)
	>>> tz0.tzname(None)
	'UCT+00:00'
	>>> tz5 = UTC('-05:30')
	>>> tz5.tzname(None)
	'UTC-05:30'
	>>> from datetime import datetime
	>>> u = datetime.utcnow().replace(tzinfo=tz0)
	>>> l1 = u.astimezone(tz8)
	>>> l2 = u.replace(tzinfo=tz8)
	>>> d1 = u - l1
	>>> d2 = u - l2
	>>> d1.seconds
	0
	>>> d2.seconds
	28800
	'''
	def __init__(self, utc):
		utc = str(utc.strip().upper())
		mt = _RE_TZ.match(utc)
		if mt:
			minus = mt.group(1)=='-'
			h = int(mt.group(2))
			m = int(mt.group(3))
			if minus:
				h, m = (-h),(-m)
			self._utcoffset = datetime.timedelta(hours=h, minutes=m)
			self._tzname = 'UTC%s' % utc
		else:
			raise ValueError('bad utc time zone')

	def utcoffset(self, dt):
		return self._utcoffset

	def dst(self, dt):
		return _TIMEDELTA_ZERO

	def tzname(self, dt):
		return self._tzname

	def __str__(self):
		return 'UTC tzinfo object (%s)' % self._tzname

	__repr__ = __str__  # return str saw by Developer
 
# all known response statuses:

_RESPONSE_STATUSES = {
	#Informational
	100: 'Continue',
	101: 'Switching Protocols',
	102:'Processing',

	# Successful
	200: 'OK',
	201: 'Created',
	202: 'Accepted',
	203: 'Non-Authoritative Information',
	204: 'No Content',
	205: 'Reset Content',
	206: 'Partial Content',
	207: 'Multi Status',
	226: 'IM Used',

	# Redirection
	300: 'Multiple Choices',
	301: 'Moved Permanently',
	302: 'Found',
	303: 'See other',
	304: 'Not Modified',
	305: 'Use Proxy',
	307: 'Temporary Redirect',

	# Client Error
	400: 'Bad Request',
	401: 'Unauthorized',
	402: 'Payment Required',
	403: 'Forbidden',
	404: 'Not Found',
	405: 'Method Not Allowed',
	406: 'Not Acceptable',
	407: 'Proxy Authentication Required',
	408: 'Request Timeout',
	409: 'Conflict',
	410: 'Gone',
	411: 'Length Required',
	412: 'Precondition Failed',
	413: 'Request Entity Too Large',
	414: 'Request URI Too Long',
	415: 'Unsupported Media Type',
	416: 'Requested Range Not Satisfiable',
	417: 'Expectation Failed',
	418: "I'm a teapot",
	422: 'Unprocessable Entity',
	423: 'Locked',
	424: 'Failed Dependency',
	426: 'Upgrade Required',

	# Server Error
	500: 'Internal Server Error',
	501: 'Not Implemented',
	502: 'Bad Gateway',
	503: 'Service Unavailable',
	504: 'Gateway Timeout',
	505: 'HTTP Version Not Supported',
	507: 'Insufficient Storage',
	510: 'Not Extended',
}

_RE_RESPONSE_STATUS = re.compile(r'^\d\d\d(\ [\w\ ]+)?$')

_RESPONSE_HEADERS = (
	'Accept-Ranges',
	'Age',
	'Allow',
	'Cache-Control',
	'Connection',
	'Content-Encoding',
	'Content-Language',
	'Content-Length',
	'Content-Location',
	'Content-MD5',
	'Content-Disposition',
	'Content-Range',
	'Content-Type',
	'Date',
	'ETag',
	'Expires',
	'Last-Modified',
	'Link',
	'Location',
	'P3P',
	'Pragma',
	'Proxy-Authenticate',
	'Refresh',
	'Retry-After',
	'Server',
	'Set-Cookie',
	'Strict-Transport-Security',
	'Trailer',
	'Transfer-Encoding',
	'Vary',
	'Via',
	'Warning',
	'WWW-Authenticate',
	'X-Frame-Options',
	'X-XSS-Protection',
	'X-Content-Type-Options',
	'X-Forwarded-Proto',
	'X-Powered-By',  # server web framework information 
	'X-UA-Compatible',
)

_RESPONSE_HEADER_DICT = dict()  # waiting to finish

_HEADER_X_POWERED_BY = ('X-Powered-By','David_Lin-Michael/1.0')

class HttpError(Exception):
	'''
	HttpError that defines http error code.

	>>> e = HttpError(404)
	>>> e.status
	'404 Not Found'
	'''
	def __init__(self, code):
		'''
		Init an HttpError with response code.
		'''
		super(HttpError, self).__init__()
		self.status = '%d %s' % (code, _RESPONSE_STATUSES[code])

	def header(self, name, value):
		if not hasattr(self, '_headers'):
			self._headers = [_HEADER_X_POWERED_BY]
		self._headers.append((name, value))

	@property
	def headers(self):
		if hasattr(self, '_headers'):
			return self._headers
		return []

	def __str__(self):
		return self.status

	__repr__ = __str__ 

class RedirectError(HttpError):
	'''
	RedirectError that defines http redirect code.

	>>> e = RedirectError(302, 'http://www.apple.com/')
	>>> e.status
	'302 Found'
	>>> e.location
	'http://www.apple.com/'
	'''
	def __init__(self, code, location):
		'''
		Init an HttpError with response code.
		'''
		super(RedirectError, self).__init__(code)
		self.location = location

	def __str__(self):
		return '%s, %s' % (self.status, self.location)

	__repr__ = __str__

def badrequest():
	'''
	Send a bad request response.

	>>> raise badrequest()
	Traceback (most recent call last):
	  ...
	HttpError: 400 Bad Request
	'''
	return HttpError(400)

def unauthorized():
	'''
	Send an unauthorized response.

	>>> raise unauthorized()
	Traceback (most recent call last):
	  ...
	HttpError: 401 Unauthorized
	'''
	return HttpError(401)

def forbidden():
	'''
	Send a forbidden response.

	>>> raise forbidden()
	Traceback (most recent call last):
	  ...
	HttpError: 403 Forbidden
	'''
	return HttpError(403)

def notfound():
	'''
	Send a not found response.

	>>> raise notfound()
	Traceback (most recent call last):
	  ...
	HttpError: 404 Not Found
	'''
	return HttpError(404)

def conflict():
	'''
	Send a conflict response.

	>>> raise conflict()
	Traceback (most recent call last):
	  ...
	HttpError: 409 Conflict
	'''
	return HttpError(409)

def internalerror():
	'''
	Send an internal error response.

	>>> raise internalerror()
	Traceback (most recent call last):
	  ...
	HttpError: 500 Internal Server Error
	'''
	return HttpError(500)

def redirect(location):
	'''
	Do permanent redirect.

	>>> raise redirect('http://www.itranswarp.com/')
	Traceback (most recent call last):
	  ...
	RedirectError: 301 Moved Permanently, http://www.itranswarp.com/
	'''
	return RedirectError(301, location)

def found(location):
	'''
	Do temporary redirect.

	>>> raise found('http://www.itranswarp.com/')
	Traceback (most recent call last):
	  ...
	RedirectError: 302 Found, http://www.itranswarp.com/
	'''
	return RedirectError(302, location)

def seeother(location):
	'''
	Do temporary redirect.

	>>> raise seeother('http://www.itranswarp.com/')
	Traceback (most recent call last):
	  ...
	RedirectError: 303 See Other, http://www.itranswarp.com/
	>>> e = seeother('http://www.itranswarp.com/seeother?r=123')
	>>> e.location
	'http://www.itranswarp.com/seeother?r=123'
	'''
	return RedirectError(303, location)

def _to_str(s):
	if isinstance(s, str):
		return s
	if isinstance(s, unicode):
		return s.encode('utf-8')
	return str(s)

def _to_unicode(s, encoding='utf-8'):
	return s.decode('utf-8')

def _quote(s, encoding='utf-8'):
	'''
	Url quote as str

	>>> _quote('http://example/test?a=1+')
	'http%3A//example/test%3Fa%3D1%2B'
	>>> _quote(u'hello world!')
	'hello%20world%21'
	'''
	if isinstance(s, unicode):
		s = s.encode(encoding)
	return urllib.quote(s)

def _unquote(s, encoding = 'utf-8'):
	'''
	Url unquote as unicode 

	>>> _unquote('http%3A//example/test%3Fa%3D1+')
	u'http://example/test?a=1+'
	'''
	return urllib.unquote(s).decode(encoding)

def get(path):
	'''
	A @get decorator.

	@get('/:id')
	def index(id):
		pass

	>>> @get('/test:id')
	... def test():
	... 	return 'ok'
	...
	>>> test.__web_route__
	'/test/:id'
	>>> test.__web_method__
	'GET'
	>>> test()
	'ok'
	'''
	def _decorator(func):
		func.__web_route__ = path
		func.__web_method__ = 'GET'
		return func
	return _decorator

def post(path):
	'''
	A @post decorator.

	>>> @post('/post/:id')
	... def testpost():
	... 	return '200'
	...
	>>> testpost.__web_route__
	'/post/:id'
	>>> testpost.__web_method__
	'POST'
	>>> testpost()
	'200
	'''
	def _decorator(func):
		func.__web_route__ = path
		func.__web_method__ = 'POST'
		return func
	return _decorator

_re_route = re.compile(r'(\:[a-zA-Z_]\w*)')  # such as /test/:id , ':id'

def _build_regex(path):
	r'''
	Convert route path to regex.

	>>> _build_regex('/path/to/:file')
	'^\\/path\\/to\\/(?P<file>[^\\/]+)$'
	>>> _build_regex('/:user/:comments/list')
    '^\\/(?P<user>[^\\/]+)\\/(?P<comments>[^\\/]+)\\/list$'
    >>> _build_regex(':id-:pid/:w')
    '^(?P<id>[^\\/]+)\\-(?P<pid>[^\\/]+)\\/(?P<w>[^\\/]+)$'
	'''
	re_list = ['^']
	var_list = []
	is_var = False
	for v in _re_route.split(path):  # (1)/ (2):user (3)/ (4):comments (5)/list
		if is_var:
			var_name = v[1:]
			var_list.append(var_name)  # var_list = [user,comments]
			re_list.append(r'(?P<%s>[^\/]+)' % var_name)
		else:
			s = ''
			for ch in v:
				if ch>='0' and ch<='9':
					s = s+ch
				elif ch>='A' and ch<='Z':
					s = s + ch
				elif ch>='a' and ch<='z':
					s = s + ch
				else:
					s = s + '\\' + ch
			re_list.append(s)
		is_var = not is_var
	re_list.append('$')
	return ''.join(re_list)

class Route(object):
	'''
	A Route object is a callable object.
	'''

	def __init__(self, func):
		self.path = func.__web_route__
		self.method = func.__web_method__
		self.is_static = _re_route.search(self.path) is None # can not find , not Pattern :id static
		if not self.is_static:
			self.route = re.compile(_build_regex(self.path)) # not static self route
		self.func = func

	def match(self, url):
		m = self.route.match(url)
		if m:
			return m.groups()
		return None

	def __call__(self, *args):
		return self.func(*args)

	def __str__(self):
		if self.is_static:
			return 'Route(static, %s, path=%s)' % (self.method, self.path)
		return 'Route(dynamic, %s, path=%s)' % (self.method, self.path)

	__repr__ = __str__

def __static_file_generator(fpath):
	BLOCK_SIZE = 8192 # why that numbers ?
	with open(fpath, 'rb') as f:
		block = f.read(BLOCK_SIZE)
		while block:
			yield block
			block = f.read(BLOCK_SIZE)

class StaticFileRoute(object):   # still don't get it

	def __init__(object):
		self.method = 'GET'
		self.is_static = False
		self.route = re.compile('^/static/(.+)$')

	def match(self, url):
		if url.startswith('/static/'):
			return (url[1:],)
		return None

	def __call__(self, *args):
		fpath = os.path.join(ctx.application.document_root, args[0])
		if not os.path.isfile(fpath):
			raise notfound()
		fext = os.path.splitext(fpath)[1]
		ctx.response.content_type = mimetypes.types_map.get(fext.lower(),'application/octet-stream')
		return _static_file_generator(fpath)

def favicon_handler():
	return static_file_handler('/favicon.ico')

class MultipartFile(object):  # as an return type for ctx.request['file']
	'''
	Multipart file storage get from request input.

	f = ctx.request['file']
	f.filename # 'test.png
	f.file # file-like object
	'''
	def __init__(self, storage):
		self.filename = _to_unicode(storage.filename)
		self.file = storage.file

if __name__=='__main__':
	sys.path.append('.')
	import doctest
	doctest.testmod()

