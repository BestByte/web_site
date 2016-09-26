import asyncio,os,inspect,logging,functools
from urlib import parse
from aiohttp import web
from apis import APIError
def get(path):
    def decorotator(func):
        @functools.wraps
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
        def wrapper(*args,**kw)：
        return func(*args,**kw)
        wrapper.__method__='POST'
        wrapper.__route__=path
    return wrapper
def get_required_kw_args(fn):
    args=[]
    params=inspect