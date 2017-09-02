import json
from nose.tools import *
from test_utils import *

async def alexa_request(client, endpoint, args=None, session=False, player_activity="IDLE"):
    application_id = "test_application"

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
            "timestamp": "string",
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

    uri = b'http://127.0.0.1:8080/alexa'

    response = await client.post(uri, data=request, headers={
        b'Content-Type': b'application/json;charset=UTF-8',
        b'Accept': b'application/json',
        b'Accept-Charset': b'utf-8',
        b'Signature': b'',
        b'SignatureCertChainUrl': b''
    })

    data = response.json()

    assert_equal(data["version"], "1.0")
    assert_in("outputSpeech", data["response"])
    assert_equal(data["response"]["outputSpeech"]["type"], "ssml")
    assert_in("ssml", data["response"]["outputSpeech"])
    assert_equal(data["shouldEndSession"], True)

    return response

@start_widgets()
@with_client
async def test_alexa(client, widgets):
    alexa_response = await alexa_request(client, "time")
    speech = alexa_response.json()["response"]["outputSpeech"]["ssml"]

    assert_equal(speech, "<speak>the date</speak>")
