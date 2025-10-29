import threading
from functools import wraps

def threaded(func):
    """
    Decorator to run a function in a separate thread.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True  # optional: thread will exit when main program exits
        thread.start()
        return thread  # return the thread in case the caller wants to join it
    return wrapper