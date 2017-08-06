import datetime
from nose.tools import *
from test_utils import *

@start_widgets('dashboard/widgets')
@with_client
async def test_time_widget(client, widgets):
    time = datetime.datetime.now().strftime("%A %B %d, %Y")

    response = await request_widget(client, 'time')
    assert_equal(response.json(), {'date':time})

    response = await request_widget(client, 'time', False)
    assert_equal(response.text, '<div>{}</div>'.format(time))
