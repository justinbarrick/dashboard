import logging
import asyncio
import functools
from json import dumps
import uvhttp.http
import uvhttp.dns
import os
import subprocess

from dashboard.server import WidgetServer

async def request_widget(client, widget, json=True, args=None):
    if json:
        encoding = b'application/json'
    else:
        encoding = b'text/html'

    method = b'GET'
    if args:
        method = b'POST'
        args = dumps(args).encode()

    url = 'http://127.0.0.1:8080/api/widgets/{}'.format(widget).encode()
    return await client.request(method, url, headers={
        b'Accept': encoding
    }, data=args)

def start_loop(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))

    return wrapper

def start_widgets(widget_path=None):
    def real_start_widgets(func):
        @start_loop
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            resolver = uvhttp.dns.Resolver(asyncio.get_event_loop())

            widgets = WidgetServer(widget_path or 'tests/widgets', resolver=resolver, settings='tests/test_data/settings.json')
            widgets.TEST = True
            await widgets.start()

            try:
                return await func(widgets, *args, **kwargs)
            finally:
                print('stopped...')
                widgets.stop()

        return wrapper

    return real_start_widgets

def with_client(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        session = uvhttp.http.Session(5, asyncio.get_event_loop())
        return await func(session, *args, **kwargs)

    return wrapper

def with_external_call(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        fifo = None
        try:
            os.mkfifo('test.fifo')
            fifo = os.open('test.fifo', os.O_RDONLY | os.O_NONBLOCK) 
            return await func(fifo, *args, **kwargs)
        finally:
            os.unlink('test.fifo')
            if fifo:
                os.close(fifo)

    return wrapper
