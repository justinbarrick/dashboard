from jinja2 import Template
from sanic import Sanic
from sanic.response import html, json

import functools
import glob
import importlib
import os

from dashboard.sonos import Sonos
import uvhttp.http
import asyncio

class WidgetServer:
    """
    Python framework for serving little widgets.

    Widgets can be stored in dashboard/widgets/.

    Any function ending with `_widget` will be routed to
    `/api/widgets/widget_name`. For example, `time_widget` is routed to
    `/api/widgets/time`.

    Widgets are loaded from `widget_path`.

    An example widget looks like:

    ```
    import datetime

    async def time_widget(request):
        return {
            "date": datetime.datetime.now().strftime("%A %B %d, %Y"),
        }
    ```

    The widget can then be served as a JSON response or via HTML.

    If HTML is requested, the returned JSON will be passed to the Jinja
    template (`$widget_path/templates/$widget_name.jinja.html`) and rendered:

    ```
    <div>{{ date }}</div>
    ```

    Static assets are served from `/static`.
    """
    def __init__(self, widget_path, sonos_api=None):
        self.__app = None
        self.__api_base = None
        self.__server = None

        self.widgets = []
        self.widget_path = widget_path
        self.app.static('/static', './static')

        self.client = uvhttp.http.Session(10, asyncio.get_event_loop())
        self.sonos = Sonos(self.client, sonos_api or '127.0.0.1')

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
        """
        Load all widgets.
        """
        for widget in glob.glob(os.path.join(self.widget_path, '*.py')):
            widget_name = os.path.splitext(widget)[0].replace('/', '.')
            module = importlib.import_module(widget_name)
            widgets = filter(lambda x: x.endswith('_widget'), dir(module))

            for widget in widgets:
                name = widget.split('_widget', 1)[0]
                self.widget(name, getattr(module, widget))
                self.widgets.append(name)

    def get_template(self, name):
        """
        Fetch a template so it can be used for rendering.
        """
        template_path = os.path.join(self.widget_path, 'templates')
        template_path = os.path.join(template_path, name + '.jinja.html')
        return Template(open(template_path).read())

    def widget(self, name, func):
        """
        Add a widget function.
        """
        template = self.get_template(name)

        @functools.wraps(func)
        async def real_widget(request, *args, **kwargs):
            encoding = request.headers.get('accept-encoding', 'html')

            response = await func(request, self, *args, **kwargs)
            if 'json' in encoding:
                return json(response)
            else:
                return html(template.render(response))

        route = os.path.join(self.api_base, name)
        self.app.add_route(real_widget, route)

    async def start(self, log_config=None):
        """
        Start the widget server.
        """
        if self.server:
            return

        self.load()
        self.app.add_route(self.index, '/')
        self.server = await self.app.create_server(host='0.0.0.0', port=8080, log_config=log_config)

    def stop(self):
        """
        Stop the widget server.
        """
        if self.server:
            self.server.close()
            self.server = None

    async def index(self, request):
        """
        Render the index page.
        """
        self.index_template = self.get_template('index')
        return html(self.index_template.render({"widgets": self.widgets}))
