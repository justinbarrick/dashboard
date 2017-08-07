from dashboard.widget import *

@refresh_every(1)
async def time_widget(request, ws):
    return {
        "date": "the date"
    }

async def default_timeout_widget(request, ws):
    return {
        "date": "the date"
    }

@refresh_every(0)
async def never_refresh_widget(request, ws):
    return {
        "date": "the date"
    }


