#
# MIT License
#
# Copyright (c) 2020 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

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

class Observed:
    """by inheriting Observed, you can watch out for changes
    in this object by calling the Observed.watch(obj) method.
    (remove from the watch list by Observed.unwatch(obj).)

    When anything changes, `obj.change_event(arg)` is called."""
    def __init__(self):
        self._observers = []

    def watch(self, obj):
        if obj not in self._observers:
            self._observers.append(obj)

    def unwatch(self, obj):
        if obj in self._observers:
            self._observers.remove(obj)

    def _fire(self, arg=None):
        """(prepared for subclasses) emits a resource-change event."""
        for obj in self._observers:
            if hasattr(obj, "change_event"):
                obj.change_event(arg)
