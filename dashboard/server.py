from jinja2 import Template
from sanic import Sanic
from sanic.response import html, json

import functools
import glob
import importlib
import os

class WidgetServer:
    def __init__(self, widget_path):
        self.__app = None
        self.__api_base = None
        self.__server = None

        self.widgets = []
        self.widget_path = widget_path
        self.index_template = self.get_template('index')
        self.app.static('/static', './static')

    @property
    def widget_path(self):
        return self.__widget_path or 'widgets'

    @widget_path.setter
    def widget_path(self, widget_path):
        self.__widget_path = widget_path

    @property
    def api_base(self):
        return self.__api_base or '/api/widgets'

    @api_base.setter
    def api_base(self, api_base):
        self.__api_base = api_base

    @property
    def server(self):
        return self.__server

    @server.setter
    def server(self, server):
        self.__server = server

    @property
    def app(self):
        if not self.__app:
            self.__app = Sanic(log_config=None)
        return self.__app

    def load(self):
        for widget in glob.glob(os.path.join(self.widget_path, '*.py')):
            widget_name = os.path.splitext(widget)[0].replace('/', '.')
            module = importlib.import_module(widget_name)
            widgets = filter(lambda x: x.endswith('_widget'), dir(module))

            for widget in widgets:
                name = widget.split('_widget', 1)[0]
                self.widget(name, getattr(module, widget))
                self.widgets.append(name)

    def get_template(self, name):
        template_path = os.path.join(self.widget_path, 'templates')
        template_path = os.path.join(template_path, name + '.jinja.html')
        return Template(open(template_path).read())

    def widget(self, name, func):
        template = self.get_template(name)

        @functools.wraps(func)
        async def real_widget(request, *args, **kwargs):
            encoding = request.headers.get('accept-encoding', 'html')

            response = await func(request, *args, **kwargs)
            if 'json' in encoding:
                return json(response)
            else:
                return html(template.render(response))

        route = os.path.join(self.api_base, name)
        self.app.add_route(real_widget, route)

    async def start(self, log_config=None):
        if self.server:
            return

        self.load()
        self.app.add_route(self.index, '/')
        self.server = await self.app.create_server(host='0.0.0.0', port=8080, log_config=log_config)

    def stop(self):
        if self.server:
            self.server.close()
            self.server = None

    async def index(self, request):
        return html(self.index_template.render({"widgets": self.widgets}))
