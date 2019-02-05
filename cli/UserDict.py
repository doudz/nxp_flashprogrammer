# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: UserDict.pyo
# Compiled at: 2010-02-17 18:13:26


class UserDict:

    def __init__(self, dict=None, **kwargs):
        self.data = {}
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)
        return

    def __repr__(self):
        return repr(self.data)

    def __cmp__(self, dict):
        if isinstance(dict, UserDict):
            return cmp(self.data, dict.data)
        return cmp(self.data, dict)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, '__missing__'):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.data[key] = item

    def __delitem__(self, key):
        del self.data[key]

    def clear(self):
        self.data.clear()

    def copy(self):
        if self.__class__ is UserDict:
            return UserDict(self.data.copy())
        import copy
        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data

        c.update(self)
        return c

    def keys(self):
        return list(self.data.keys())

    def items(self):
        return list(self.data.items())

    def iteritems(self):
        return iter(self.data.items())

    def iterkeys(self):
        return iter(self.data.keys())

    def itervalues(self):
        return iter(self.data.values())

    def values(self):
        return list(self.data.values())

    def has_key(self, key):
        return key in self.data

    def update(self, dict=None, **kwargs):
        if dict is None:
            pass
        if isinstance(dict, UserDict):
            self.data.update(dict.data)
        if isinstance(dict, type({})) or not hasattr(dict, 'items'):
            self.data.update(dict)
        for k, v in list(dict.items()):
            self[k] = v

        if len(kwargs):
            self.data.update(kwargs)
        return

    def get(self, key, failobj=None):
        if key not in self:
            return failobj
        return self[key]

    def setdefault(self, key, failobj=None):
        if key not in self:
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        return self.data.pop(key, *args)

    def popitem(self):
        return self.data.popitem()

    def __contains__(self, key):
        return key in self.data

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value

        return d


class IterableUserDict(UserDict):

    def __iter__(self):
        return iter(self.data)


import _abcoll
_abcoll.MutableMapping.register(IterableUserDict)

class DictMixin:

    def __iter__(self):
        for k in list(self.keys()):
            yield k

    def has_key(self, key):
        try:
            value = self[key]
        except KeyError:
            return False

        return True

    def __contains__(self, key):
        return key in self

    def iteritems(self):
        for k in self:
            yield (
             k, self[k])

    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        for _, v in self.items():
            yield v

    def values(self):
        return [ v for _, v in self.items() ]

    def items(self):
        return list(self.items())

    def clear(self):
        for key in list(self.keys()):
            del self[key]

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default

        return default

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError('pop expected at most 2 arguments, got ' + repr(1 + len(args)))
        try:
            value = self[key]
        except KeyError:
            if args:
                return args[0]
            raise

        del self[key]
        return value

    def popitem(self):
        try:
            k, v = next(iter(self.items()))
        except StopIteration:
            raise KeyError('container is empty')

        del self[k]
        return (
         k, v)

    def update(self, other=None, **kwargs):
        if other is None:
            pass
        if hasattr(other, 'iteritems'):
            for k, v in other.items():
                self[k] = v

        if hasattr(other, 'keys'):
            for k in list(other.keys()):
                self[k] = other[k]

        for k, v in other:
            self[k] = v

        if kwargs:
            self.update(kwargs)
        return

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __repr__(self):
        return repr(dict(iter(self.items())))

    def __cmp__(self, other):
        if other is None:
            return 1
        if isinstance(other, DictMixin):
            other = dict(iter(other.items()))
        return cmp(dict(iter(self.items())), other)

    def __len__(self):
        return len(list(self.keys()))