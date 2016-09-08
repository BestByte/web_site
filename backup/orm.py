#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
#logging.basicConfig(level=logging.info)
import asyncio,os,json,time
from datetime import datetime
from aiohttp import web
import aiomysql
@asyncio.coroutine
def create_pool(loop,**kw):
    logging.info('create database connection pool...')
    global _pool
    _pool=yield from aiomysql.create_pool(host=kw.get('host','localhost'),
    port=kw.get('port',2206),
    user=kw['user'],
    password=kw['password'],
    db=kw['db'],
    charsetset=charset.get('charset','utf8'),
    autocommit=kw.get('autocommit',True),
    maxsize=kw.get('maxsize',10),
    minsize=kw.get('minsize',1)
    loop=loop 
    )
@asyncio.coroutine
def select(sql,args,size=None):
    log(sql, args)
    global _pool
    with (yield from _pool) as conn:
        cur=yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?','%s'),args or ())
        if size:
            rs=yield from cur.fetchmany(size)
        else:
            rs=yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows retuns:%s'%len(rs))
        return rs
@asyncio.coroutine
def execute(sql,args):
    log(sql)
    with (yield from _pool) as conn:
        try:
            cur=yield from conn.cursor()
            yield from cur.execute(sql.replace('?','%s'),args)
            affected=cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected
    
def log(sql , args=()):
    logging.info('SQL:%s'%sql)
def create_args_string(num):
    L=[]
    for n in range(num):
        L.append('?')
    return ','.join(L)
