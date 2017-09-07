import os
from nose.tools import *
from test_utils import *

@start_widgets('dashboard/widgets')
@with_external_call
@with_client
async def test_cec_tv_on(client, fifo, widgets):
    response = await request_widget(client, 'tv_on')
    assert_equal(response.json(), {"tv": True})
    assert_equal(os.read(fifo, 1024), b'on 0\nas\n')

@start_widgets('dashboard/widgets')
@with_external_call
@with_client
async def test_cec_tv_off(client, fifo, widgets):
    response = await request_widget(client, 'tv_off')
    assert_equal(response.json(), {"tv": False})
    assert_equal(os.read(fifo, 1024), b'standby 0\n')
