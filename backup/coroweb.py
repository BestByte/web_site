import asyncio,os,inspect,logging,functools
from urlib import parse
from aiohttp import web
from apis import APIError
from asyncio.tasks import async
def get(path):
    def decorotator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method='GET'
        wrapper.__route__=path
        return wrapper
    return decorator
def post(path):
    '''
    define decorote @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__='POST'
        wrapper.__route__=path
    return wrapper
def get_required_kw_args(fn):
    args=[]
    params=inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind==inspect.Parameter.KEYWORD_ONLY and param.default==args.append(name):
			return tuple(args)
def get_named_kw_args(fn):
	args=[]
	params=inspect.signature(fn).parameters
	for name,param in params.items():
		if param.kind==inspect.Parameter.KEYWORD_ONLY:
			args.append(name)
	return tuple(args)
def has_named_kw_args(fn):
	params=inspect.signature(fn).parameters
	for name,param in params.items():
		if param.kind==inspect.Parameter.KEYWORD_ONLY:
			return True
def has_var_kw_arg(fn):
	params=inspect.signature(fn).parameters
	for name,param in params.items():
		if param.kind==inspect.Parameter.VAR_KEYWORD:
			return True
def has_request_arg(fn):
	sig=inspect.signature(fn)
	params=sig.parameters
	found=False
	for name,param in params.items():
		if name=='request':
			found=True
			continue
		if found and (param.kind!=inspect.Parameter.VAR_POSITIONAL and param.kind!=inspect.Parameter.KEYWORD_ONLY and param.kind!=inspect.Parameter.VAR_KEYWORD):
			raise ValueError('request parameter must be the last named parameter in function:%s%s'%(fn.__name__,str(sig)))
	return found
class RequestHandler():
	def _init__(self,app,fn):
		self._app=app
		self._func=fn
		self._has_request_arg=has_request_arg(fn)
		self._has_var_kw_arg=has_var_kw_arg(fn)
		self._has_named_kw_args=has_named_kw_args(fn)
		self._named_kw_args=get_named_kw_args(fn)
		self._required_kw_ars=get_required_kw_args(fn)
	@asyncio.coroutine
	def __call__(self,request):
		kw=None
		if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_ars:
			








