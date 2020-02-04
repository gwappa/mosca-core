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
