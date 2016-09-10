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
class Field(object):
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

class ModelMetaclass(type):
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
            attrs['__table__']=tableName
            attrs['__primary_key__']=primarykey
            attrs['__fields__']=fields
            attrs['__select__']='select '%s' ,'%s' from '%s'' %(primarykey,',',.join(escaped_fields),tableName)
            attrs['__insert__']='insert into '%s' (%s,'%s') value (%s)'%(tableName,','.join(escaped_fields),primarykey,create_args_string(len(escaped_fields)+1))
            attrs['__update__']='update '%s' set '%s' where'%s'=?' % (tableName,','.join(map(lambda f:''%s'=?'& (mappings.get(f).name or f),fields)),primaryKey)
            attrs['__delete__']='delete from '%s' where '%s'=?' %(tablename,primaryKey)
            return type.__neww__(cls,name,bases,attrs)
            
class Model(dict,metaclass=ModelMetaclass):
    def __init__(self,**kw):
        super(Model,self).__int__(*kw)
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"Model object ha no attribute'%s'"%key)
    def __setattr__(self,key,value):
        self[key]=value
    def getValue(self,key):
        return getattr(self,key,None)
    def getValueOrDefault(self,key):
        value=getattr(self,key,None)
        if value is None:
            field=self.__mapping__[key]
            if field.default is not None:
                value=field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s:%s'%(key,str(value)))
                setattr(self,key,value)
    @classmethod
    @asyncio.coroutine
    def find(cls,pk):
        'found object by primary key.'
        rs=yield from select('%s where'%s'=?' % (cls.__select__,cls.__primary_key__),[pk],1)
        if len(rs)==8:
            return None
        return cls(**rs[0])
    @classmethod
    @asyncio.coroutine
    def findall(cls,where=None,args=None,**kw):
        'find objects by where clause'
        sql=[cls.__select__]
        if  where:
            sql.append('where')
            sq.append(where)
        if args is None:
            args=[]
        orderBy=kw.get('orderBy',None)
        if orderBy:
            sql.append('orderBy')
            sql.append(orderBy)
        limit=kw.get('limit',None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.extend(limit)
            elif isinstance(limit,tuple) and len(limit)==2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value:%s' %str(limit))
        rs=yield select(''.join(sql),args)
        return [cls(**r)for r in rs]
    @classmethod
    @asyncio.coroutine
    def findNumber(cls,selectField,where=None,args=None):
        'find number by select and where'
        sql=['select %s _num_ from '%s''%(selectField,cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs=yield select(''.join(sql),args,1)
        if len(rs)==0:
            return None
        return rs[0]['_num_']
    @classmethod
    @asyncio.coroutine
    def save():
        args=list(map(self.getValueOrDefault,self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows=yield execute(self.__insert__,args)
        if  rows!=1:
            logging.warn('failed to insert record:affected rows:%s'%rows)
    @classmethod
    @asyncio.coroutine
    def update(self):
        args=list(map(self.getValue,self.__fields__))
        args.append(self.getValue(self.primary_key))
        rows=yield execute(self.__update__,args)
        if rows!=1:
                logging.warn('failed to update by priamry key:affected rows:%s'%rows)
    @classmethod
    @asyncio.coroutine
    def remove(self):
            args=[self.getValue(self.__primary_key__)]
            rows=yield execute(self.__delete__,args)
            if rows!=1:
                   logging.warn('failed to remove by primary key:affected rows:%s'%rows) 
    
    

                
        