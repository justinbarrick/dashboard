from jinja2 import Template
from OpenSSL.crypto import FILETYPE_PEM, load_certificate, verify
from sanic import Sanic
from sanic.response import html, json
from urllib.parse import urljoin
from datetime import datetime

import base64
import functools
import glob
import importlib
import logging
import os
import ssl

from dashboard.widget_context import WidgetContext
import uvhttp.http
import asyncio

ISO = "%Y-%m-%dT%H:%M:%SZ"

class WidgetServer:
    """
    Python framework for serving little widgets.

    Widgets can be stored in ``dashboard/widgets/``.

    Any function ending with ``_widget`` will be routed to
    ``/api/widgets/widget_name``. For example, ``time_widget`` is routed to
    ``/api/widgets/time``.

    Widgets are loaded from ``widget_path``.

    An example widget looks like::

        import datetime

        async def time_widget(request):
            return {
                "date": datetime.datetime.now().strftime("%A %B %d, %Y"),
            }

    The widget can then be served as a JSON response or via HTML.

    If HTML is requested, the returned JSON will be passed to the Jinja
    template (``$widget_path/templates/$widget_name.jinja.html``) and rendered::

        <div>{{ date }}</div>

    Static assets are served from ``/static``.
    """
    def __init__(self, widget_path):
        self.__app = None
        self.__api_base = None
        self.__server = None

        self.TEST = False
        self.cert_base = 'https://s3.amazonaws.com/echo.api/'
        self.__certs = {}

        self.widgets = {}
        self.widget_path = widget_path

        self.app.config.LOGO = None
        self.app.static('/static', './static')
        self.app.static('/css', './dashboard/widgets/templates/css/')
        self.app.add_route(self.skill_endpoint, '/alexa', methods=['POST'])

        self.wc = WidgetContext()

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
            self.__app = Sanic()
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

                widget_func = getattr(module, widget)

                self.widget(name, widget_func)
                self.widgets[name] = widget_func

    def get_template(self, name, ssml=False):
        """
        Fetch a template so it can be used for rendering.
        """
        template_path = os.path.join(self.widget_path, 'templates')
        ext = '.jinja.html' if not ssml else '.jinja.ssml'
        template_path = os.path.join(template_path, name + ext)

        if not os.path.exists(template_path):
            return False

        return Template(open(template_path).read())

    def widget(self, name, func):
        """
        Add a widget function.
        """

        @functools.wraps(func)
        async def real_widget(request, *args, **kwargs):
            encoding = request.headers.get('accept', 'html')

            response = await func(request, self.wc, *args, **kwargs)
            if 'json' in encoding:
                return json(response)
            else:
                template = self.get_template(name)
                if template:
                    return html(template.render(response))
                else:
                    return html('', status=404)

        route = os.path.join(self.api_base, name)
        self.app.add_route(real_widget, route)

    async def start(self):
        """
        Start the widget server.
        """
        if self.server:
            return

        self.load()
        self.app.add_route(self.index, '/')
        self.server = await self.app.create_server(host='0.0.0.0', port=8080)

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
        return html(self.index_template.render({
            "widgets": dict([
                (name, {"frequency": getattr(func, 'frequency', None)}) for name, func in self.widgets.items() if self.get_template(name)
            ])
        }))

    async def load_cert(self, request):
        ssl_ctx = ssl.create_default_context()
        if self.TEST:
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

        cert_url = request.headers['SignatureCertChainUrl']
        if urljoin(cert_url, '.') != self.cert_base:
            return False

        if cert_url in self.__certs:
            return self.__certs[cert_url]

        cert_response = await self.wc.client.get(cert_url.encode(), ssl=ssl_ctx)
        cert = load_certificate(FILETYPE_PEM, cert_response.text)
        self.__certs[cert_url] = cert
        return cert

    async def verify_certificate(self, request):
        signature = base64.b64decode(request.headers['Signature'])
        cert = await self.load_cert(request)

        try:
            verify(cert, signature, request.body, 'sha1')
            return True
        except:
            return False

    async def skill_endpoint(self, request):
        """
        Widgets can be exposed as Alexa skills by creating a SSML file
        indicating how to render the response.

        The SSML file should be in the templates file as
        ``widget_name.jinja.ssml``.
        """
        verify_status = await self.verify_certificate(request)
        if not verify_status:
            logging.error('Could not verify request.')
            return json({}, status=500)

        body = request.json

        ts = datetime.strptime(body["request"]["timestamp"], ISO)
        if (datetime.now() - ts).total_seconds() > 150:
            logging.error('Replay detected.')
            return json({}, status=500)

        if body["request"]["type"] != "IntentRequest":
            logging.error('Request is not an IntentRequest.')
            return json({}, status=500)

        intent = body["request"]["intent"]

        if intent["name"] not in self.widgets:
            logging.error('Widget not found.')
            return json({}, status=500)

        response = await self.widgets[intent["name"]](request, self.wc)
        ssml_template = self.get_template(intent["name"], ssml=True)

        rendered = ssml_template.render(response).replace('&', 'and')

        response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": rendered 
                },
                "shouldEndSession": True
            },
        }

        logging.error('Sending: {}'.format(str(response)))
        return json(response)
