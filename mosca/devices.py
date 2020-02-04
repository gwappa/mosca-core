from . import utils as _utils

TYPES = dict()

class Device:
    """base interface class for a physical device."""
    @classmethod
    def get_instance(cls, name=None, **params):
        return _utils.Result.failure("not implemented")

    @property
    def name(self):
        """must return the name of a device (as it is displayed)."""
        return "(no name)"

    @property
    def ID(self):
        """must return a value to identify the device (across drivers)."""
        return None

    def __eq__(self, other):
        return isinstance(other, Device) and (self.ID == other.ID)

def load(device_config):
    """loads a device interface based on `device_config`.
    returns a Result object."""
    if "type" not in device_config.keys():
        return _utils.Result.failure(f"\"type\" key not found in device config: {device_config}")
    typ    = device_config["type"]
    name   = device_config.get("name", None)
    params = device_config.get("params", {})
    if typ not in TYPES.keys():
        return _utils.Result.failure(f"unknown device type: \"{typ}\"")
    return TYPES[typ].get_instance(name, **params)

def register(key, cls):
    """returns a Result object, with the specified key as the value."""
    if not issubclass(cls, Device):
        return _utils.Result.failure("devices.register() expected a Device subclass class-object, "
                                    f"found {cls}")
    TYPES[key] = cls
    return _utils.Result.success(key)

class DummyDevice(Device):
    @classmethod
    def get_instance(cls, name=None):
        return _utils.Result.success(cls(name))

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def ID(self):
        return repr(self)

    def __repr__(self):
        return f"DummyDevice({repr(self._name)})"

_ret = register("dummy", DummyDevice)
if _ret.success == False:
    raise RuntimeError("failed to register the dummy device interface")
