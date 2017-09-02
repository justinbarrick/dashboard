import functools

def refresh_every(frequency):
    """
    Widget wrapper that sets the widget to refresh every ``frequency`` seconds.

    The ``frequency`` is available as ``frequency`` in the widget options in the index
    template.

    A widget with a ``frequency`` of ``None`` should be refreshed at the default interval.
    A widget with a ``frequency`` of ``0`` should never be refreshed.
    A widget with a ``frequency`` of ``n`` should be refreshed every ``n`` seconds.
    """
    def wrapper(func):
        @functools.wraps(func)
        async def real_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        real_wrapper.frequency = frequency
        return real_wrapper

    return wrapper

def methods(methods):
    """
    Widget wrapper that sets the widget to refresh every ``frequency`` seconds.

    The ``frequency`` is available as ``frequency`` in the widget options in the index
    template.

    A widget with a ``frequency`` of ``None`` should be refreshed at the default interval.
    A widget with a ``frequency`` of ``0`` should never be refreshed.
    A widget with a ``frequency`` of ``n`` should be refreshed every ``n`` seconds.
    """
    def wrapper(func):
        @functools.wraps(func)
        async def real_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        real_wrapper.methods = methods
        return real_wrapper

    return wrapper
