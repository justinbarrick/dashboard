import datetime

async def time_widget(request):
    """
    Return the current time.
    """
    return {
        "date": datetime.datetime.now().strftime("%A %B %d, %Y"),
    }
