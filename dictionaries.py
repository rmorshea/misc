from weakref import ref as weakref

class refdict(dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        if not isinstance(key, weakref):
            key = weakref(key)
        s = super(refdict, self)
        s.__setitem__(key, value)

    def __getitem__(self, key):
        if isinstance(key, weakref):
            return super(refdict, self).__getitem__(key)
        for ref in [r for r in self]:
            if ref() is None:
                del self[ref]
            elif key is ref():
                return super(refdict, self).__getitem__(ref)
        raise KeyError(str(key))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                "got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

    def _trim(self):
        for r in [r for r in self]:
            if r() is None:
                del self[r]

    def keys(self):
        self._trim()
        return [ref() for ref in self]

    def values(self):
        self._trim()
        get = super(refdict, self).__getitem__
        return [get(ref) for ref in self]

    def items(self):
        self._trim()
        keys = [ref() for ref in self]
        get = super(refdict, self).__getitem__
        values = [get(ref) for ref in self]
        return zip(keys, values)