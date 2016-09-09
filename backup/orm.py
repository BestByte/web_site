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
class Field():
    def __init__(self, name,column_type,primary_key,default):
        self.name=name
        self.column_type=column_type
        self.primarary_key=primarary_key
        self.default=default
    def __str__(self):
        return '<%s,%s:%s>'%(self.__class__.__name__,self.column_type,self.name)
class FloatField(Field):
    def __init__(self,name=None,primary_key=False,default=0):
        super().__init__(name,'real',primary_key,default)
class StringField(Field):
    def __init__(self,name=None,primary_key=False,default=None,ddl='varchar(100)'):
        super().__init__(name,ddl,primary_key,default)
class IntegerField(Field):
    def __init__(self,name=None,primary_key=False,default=0):
        super().__init__(name,'bigint',priamry_key,default)
class BooleanField(Field):
    def __init__(self,name=None,primary_key=False,default=0):
        super().__init__(name,'boolean',False,default)
class TextField(Field):
    def __init__(self,name=None,default=None):
        super().__init__(name,'text',False,default)
class ModelMetaClass(type):
    def __new__(cls,name,bases,attrs):
        if name=='Model':
            return type.__new__(cls,name,bases,attrs)
            tableName=attrs.get('__table__',name) or name
            logging.info("found Model:%s (table:%s)"% (name,tableName))
            mappings =dict()
            fields=[]
            primarykey=None
            for k,v in attrs.items():
                if isinstance(v, Field):
                    logging.info('found mapping:%s==>%s'%(k,v))
                    mapping=k
                    if v.primary_key:
                        # found main key()
                        if primary_key:
                            raise AttributeError("Duplicate primary key for field:%s"% k )
                        primarykey =k
                    else:
                        fields.append(k)
            if not primarykey:
                raise AttributeError("primary key not found")
            for k in mapping.keys():
                attrs.pop(k)
            escaped_fields=list(map(lambda f:'%s'% f,fields))
            attrs['__mapping__']=mappings
                
        