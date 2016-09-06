#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')
import asyncio,os,json,time
from datetime import datetime
from aiohttp import web
def index(request):
    return web.Response(body=b'<h1>Awesome<h1>')
@asyncio.coroutine
def init(loop):
    app=web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv=yield from loop.create_server(app.make_handler(),'127.0.0.1',8000)
    logging.info("Server started at http://127.0.01:9000")
    return srv
loop=asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
#loop.run_forver()