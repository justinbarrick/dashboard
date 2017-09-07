import subprocess

def shell(command):
    return subprocess.check_output(command, shell=True)

async def tv_on_widget(request, wc):
    """
    Widget to turn on the TV.
    """
    await wc.run(shell, "echo on 0 |cec-client -s -d 1")
    await wc.run(shell, "echo as |cec-client -s -d 1")
    return { "tv": True }

async def tv_off_widget(request, wc):
    """
    Widget to turn off the TV.
    """
    await wc.run(shell, "echo standby 0 |cec-client -s -d 1")
    return { "tv": False }
