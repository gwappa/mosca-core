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
import collections as _collections

class Resource:
    """base structure for managed physical resource.

    you can watch out for changes in resource availability
    by calling the Resource.watch(obj) method.
    (remove from the watch list by Resource.unwatch(obj).)

    When resource availability changes, `obj.resource_changed()`
    is called."""

    @staticmethod
    def build(cfg):
        if not _utils.mappable(cfg):
            raise ValueError(f"Resource.build() expects a dict, got {cfg.__class__}")
        out = _collections.OrderedDict()
        for key, val in cfg.items():
            if val is None:
                out[key] = ResourceElement()
            else:
                out[key] = Resource.build(val)
        return out

    def __init__(self):
        self._observers = []

    def watch(self, obj):
        if obj not in self._observers:
            self._observers.append(obj)

    def unwatch(self, obj):
        if obj in self._observers:
            self._observers.remove(obj)

    def _fire(self):
        """(prepared for subclasses) emits a resource-change event."""
        for obj in self._observers:
            if hasattr(obj, "resource_changed"):
                obj.resource_changed()

    def retain(self, user):
        """returns a Result instance with this Resource."""
        if not self.is_available(user):
            return _utils.Result.failure(f"resource already used")
        self._register(user)
        self._fire()
        return _utils.Result.success(self)

    def release(self):
        self._unregister()
        self._fire()

    def _register(self, user):
        """registers a new user (without any checking)"""
        raise NotImplementedError(f"{self.__class__.__name__}._register")

    def _register(self):
        """un-registers any existing user(s)"""
        raise NotImplementedError(f"{self.__class__.__name__}._unregister")

    def is_available(self, user=None):
        """tests if this resource is available for the specified user."""
        return False # False on default

    def __add__(self, other):
        if not isinstance(other, Resource):
            raise ValueError(f"cannot add {other.__class__} to Resource")
        if isinstance(self, ResourceGroup):
            items1 = tuple(self.values())
        else:
            items1 = (self,)
        if isinstance(other, ResourceGroup):
            items2 = tuple(other.values())
        else:
            items2 = (other,)
        return ResourceSet(*(items1 + items2))

class ResourceElement(Resource):
    """the unit class for physical resource."""
    def __init__(self):
        super().__init__()
        self._user = None

    def _register(self, user):
        """registers a new user (without any checking)"""
        self._user = user

    def _unregister(self):
        """un-registers any existing user(s)"""
        self._user = None

    def is_available(self, user=None):
        """tests if this resource is available for the specified user."""
        if self._user is None:
            return True
        elif user is None:
            # already used, and no specific potential user specified
            return False
        else:
            # can return true if the paths are the same
            return (self._user.path == user.path)

class ResourceGroup(Resource):
    """an abstract class for representing a group of Resources.
    its sub-components are accessed via the `values()`` method."""
    def __init__(self):
        super().__init__()
        self.__changing = False

    def is_available(self, user=None):
        """tests if this resource is available for the specified user."""
        return all(comp.is_available(user) for comp in self.values())

    def resource_changed(self):
        """called from the underlying resource sub-components.
        fires a resource-change event only when this object itself
        is not directly responsible for the change."""
        if self.__changing == False:
            self._fire()

    def _register(self, user):
        """registers a new user (without any checking)"""
        self.__changing = True
        for comp in self.values():
            comp._register(user)
        self._fire()
        self.__changing = False

    def _unregister(self):
        """un-registers any existing user(s)"""
        self.__changing = True
        for comp in self.values():
            comp._unregister()
        self._fire()
        self.__changing = False

class ResourceSet(ResourceGroup):
    """represents a set of resources (without any ordering or mapping)."""
    def __init__(self, *subcomponents):
        super().__init__()
        self._children = tuple(set(subcomponents))

    def values(self):
        return self._children

class ResourceMap(ResourceGroup):
    """represents a map of Resources."""
    def __init__(self, subcomponents):
        super().__init__()
        self._children = _collections.OrderedDict()
        for name, item in subcomponents.items():
            if not isinstance(item, Resource):
                raise ValueError(f"item \"{name}\" is not a Resource: {item.__class__}")
            self._children[name] = item
            item.watch(self)
        self.__getitem__ = self._children.__getitem__
        self.keys        = self._children.keys
        self.values      = self._children.values

    def __getattr__(self, name):
        if name in self.keys():
            return self._children[name]
        else:
            raise AttributeError(name)
