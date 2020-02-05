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

from . import utils as _utils
from . import devices as _devices

VERSION_STR = "0.2a1"

class Setup:
    @classmethod
    def setup(cls, cfg):
        if _utils.mappable(cfg):
            return cls.setup([cfg])
        elif iterable(cfg):
            obj = cls()
            for device_config in cfg:
                ret = obj.load(device_config)
                if ret.success == False:
                    _utils.warn(ret.message)
            return obj
        else:
            raise ValueError(f"unknown config object type: {cfg.__class__}")

    def __init__(self):
        self._devices = []

    @property
    def devices(self):
        return self._devices

    def __contains__(self, device):
        return device.ID in [d.ID for d in self._devices]

    def load(self, device_config):
        """loads a device interface based on `device_config`.
        returns a Result object."""
        ret = _devices.load(device_config)
        if ret.success == False:
            return _utils.Result.failure(f"failed to load a device : {ret.message} (config={device_config})")
        dev = ret.value
        if dev in self._devices:
            return _utils.Result.failure(f"duplicate instance: {dev}")
        self._devices.append(dev)
        return _utils.Result.success(dev)
