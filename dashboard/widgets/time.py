import datetime

async def time_widget(request):
    return {
        "date": datetime.datetime.now().strftime("%A %B %d, %Y"),
    }
