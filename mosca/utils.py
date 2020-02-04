import sys as _sys
import collections as _collections

def warn(msg, end="\n", flush=True):
    print(f"***{msg}", file=_sys.stderr, end=end, flush=flush)

def mappable(obj):
    return all(hasattr(obj, attr) and callable(getattr(obj, attr)) \
                for attr in ("keys", "values", "items"))

class Result(_collections.namedtuple("Result",
                    ("success", "message", "value"))):
    @classmethod
    def success(cls, value=None, message=None):
        if message is None:
            message = "success"
        return cls(True, message, value)

    @classmethod
    def failure(cls, message, value=None):
        if message is None:
            message = "failed (details unknown)"
        return cls(False, message, value)
