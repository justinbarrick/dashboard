import base64
import json
import datetime
from nose.tools import *
from test_utils import *
from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, sign
from uvhttp.utils import HttpServer
from sanic.response import html
from dashboard.server import ISO

class AlexaServer(HttpServer):
    def add_routes(self):
        self.cert_requested = False
        self.app.add_route(self.cert, '/cert.pem')

    def cert(self, request):
        self.cert_requested = True
        return html(open('tests/test_data/cert.pem').read())

async def alexa_request(widgets, client, endpoint, args=None, session=False, player_activity="IDLE", bad=False, old=False):
    application_id = "test_application"

    if not old:
        now = datetime.datetime.now()
    else:
        now = datetime.datetime.now() - datetime.timedelta(seconds=151)

    user = {
        "userId": "string",
        "accessToken": "string",
        "permissions:": {
            "consentToken": "string"
        }
    }

    request = {
        "version": "1.0",
        "context": {
            "System": {
                "application": {
                    "applicationId": application_id
                },
                "user": user,
                "device": {
                    "deviceId": "string",
                    "supportedInterfaces": {
                        "AudioPlayer": {}
                    }
                },
                "apiEndpoint": "https://api.amazonalexa.com/"
            },  
            "AudioPlayer": {
                "token": "string",
                "offsetInMilliseconds": 0,
                "playerActivity": player_activity
            }
        },
        "request": {
            "type": "IntentRequest",
            "requestId": "string",
            "timestamp": now.strftime(ISO),
            "locale": "en-US",
            "intent": {
                "name": endpoint,
                "confirmationStatus": "string",
                "slots": {}
            }
        }
    }

    if args:
        for key, value in args.items():
            request["request"]["intent"]["slots"][key] = {
                "name": key,
                "value": value,
                "confirmationStatus": "NONE"
            }

    if session:
        request["session"] = {
            "new": True,
            "sessionId": "string",
            "application": {
                "applicationId": application_id
            },
            "attributes": {
                "string": {}
            },
            "user": user
        }

    request = json.dumps(request).encode()

    key = open('tests/test_data/key.pem', 'rb').read()
    signing = load_privatekey(FILETYPE_PEM, key)
    signature = sign(signing, request, 'sha1')

    if bad:
        signature = signature + b'abc'

    uri = b'http://127.0.0.1:8080/alexa'

    server = AlexaServer()
    await server.start()

    addr = 'https://{}:{}/'.format(server.https_host, server.https_port)

    widgets.cert_base = addr

    try:
        response = await client.post(uri, data=request, headers={
            b'Content-Type': b'application/json;charset=UTF-8',
            b'Accept': b'application/json',
            b'Accept-Charset': b'utf-8',
            b'Signature': base64.b64encode(signature),
            b'SignatureCertChainUrl': (addr + 'cert.pem').encode()
        })
    finally:
        server.stop()

    if bad or old:
        assert_equal(response.status_code, 500)
        return response

    data = response.json()

    assert_equal(data["version"], "1.0")
    assert_equal(data["sessionAttributes"], {})
    assert_in("outputSpeech", data["response"])
    assert_equal(data["response"]["outputSpeech"]["type"], "SSML")
    assert_in("ssml", data["response"]["outputSpeech"])
    assert_equal(data["response"]["shouldEndSession"], True)

    assert_equal(server.cert_requested, True)

    return response

@start_widgets()
@with_client
async def test_alexa(client, widgets):
    alexa_response = await alexa_request(widgets, client, "alexa")
    speech = alexa_response.json()["response"]["outputSpeech"]["ssml"]

    assert_equal(speech, "<speak>and the date</speak>")

@start_widgets()
@with_client
async def test_alexa_only(client, widgets):
    alexa_response = await alexa_request(widgets, client, "no_ui")
    speech = alexa_response.json()["response"]["outputSpeech"]["ssml"]

    assert_equal(speech, "<speak>and the date</speak>")

@start_widgets()
@with_client
async def test_alexa_bad_signature(client, widgets):
    await alexa_request(widgets, client, "alexa", bad=True)

@start_widgets()
@with_client
async def test_alexa_old(client, widgets):
    await alexa_request(widgets, client, "alexa", old=True)
