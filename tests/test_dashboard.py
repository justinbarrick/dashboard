from nose.tools import *
from test_utils import *
from hashlib import md5
import run

@start_widgets()
async def test_dashboard_get_template(widgets):
    assert_equal(widgets.widget_path, 'tests/widgets')

    template = widgets.get_template('time')
    assert_equal(template.render({'date': 'hello'}), '<div>hello</div>')

@start_widgets()
@with_client
async def test_dashboard_index(client, widgets):
    response = await client.get(b'http://127.0.0.1:8080/')
    assert_in('<html>', response.text)
    assert_in('time - 1', response.text)
    assert_in('default_timeout - None', response.text)
    assert_in('never_refresh - 0', response.text)
    assert_in('alexa - None', response.text)
    assert_not_in('no_ui', response.text)

@start_widgets()
@with_client
async def test_dashboard_html(client, widgets):
    response = await client.get(b'http://127.0.0.1:8080/api/widgets/time')
    assert_equal(response.text, '<div>the date</div>')

@start_widgets()
@with_client
async def test_dashboard_json(client, widgets):
    response = await client.get(b'http://127.0.0.1:8080/api/widgets/time', headers={
        b'Accept': b'application/json'
    })

    assert_equal(response.json(), {'date':'the date'})

@start_loop
@with_client
async def test_dashboard_run(client):
    widgets = await run.main()

    try:
        response = await client.get(b'http://127.0.0.1:8080/')
        assert_in('<html>', response.text)
        assert_in('sonos', response.text)
    finally:
        widgets.stop()

@start_widgets()
@with_client
async def test_dashboard_static(client, widgets):
    response = await client.get(b'http://127.0.0.1:8080/static/favicon.ico')
    assert_equal(md5(response.content).hexdigest(), '3046037cd9f72499b31c5e10da7655d5')

@start_widgets()
@with_client
async def test_dashboard_refresh_every_decorator(client, widgets):
    assert_equal(widgets.widgets['time'].frequency, 1)
    assert_equal(widgets.widgets['never_refresh'].frequency, 0)
    assert_equal(hasattr(widgets.widgets['default_timeout'], 'frequency'), False)
