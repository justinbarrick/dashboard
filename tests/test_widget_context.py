from test_utils import start_widgets
from nose.tools import *
import os

def run_me(arg):
    return 'child', os.getpid(), arg

@start_widgets()
async def test_process_runner(widgets):
    result = await widgets.wc.run(run_me, 4)
    assert_equal(result[0], 'child')
    assert_not_equal(result[1], os.getpid())
    assert_equal(result[2], 4)
