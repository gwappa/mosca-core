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

from .. import utils as _utils

class NoPhysicalResource:
    """dummy resource object."""
    def is_available(self, user):
        return True

class Channel(_utils.Observed):
    """the base channel class."""
    def __init__(self, name, device, ID, resource=None):
        if name is None:
            name = ""
        self.name      = name
        self._device   = device
        self._ID       = ID
        if resource is not None:
            self._resource.watch(self)
            self._resource = resource
        else:
            self._resource = NoPhysicalResource()
        self._active   = False

    def change_event(self, arg=None):
        self._fire()

    @property
    def name(self):
        return self._name

    @name.setter
    def set_name(self, name):
        self._name = name

    @property
    def device(self):
        return self._device

    @property
    def ID(self):
        return self._ID

    @property
    def enabled(self):
        return self._resource.is_available(self)

    @property
    def is_digital(self):
        return False

    @property
    def is_analog(self):
        return False

    @property
    def is_input(self):
        return False

    @property
    def is_output(self):
        return False

class InputChannel(Channel):
    """input channel class."""
    def __init__(self, name, device, ID, resource=None):
        super().__init__(name, device, ID, resource=resource)

    @property
    def is_input(self):
        return True

class DigitalInput(InputChannel):
    """represents a digital input port."""
    def __init__(self, name, device, ID, resource=None):
        super().__init__(name, device, ID, resource=resource)

    @property
    def is_digital(self):
        return True

class AnalogInput(InputChannel):
    """represents an analog input port."""
    def __init__(self, name, device, ID, resource=None):
        super().__init__(name, device, ID, resource=resource)

    @property
    def is_analog(self):
        return True
