from traitlets import *
from weakref import ref as weakref
from dictionaries import refdict as rdict

from functools import wraps
from threading import local

def recursion_detector(func):
    func._thread_locals = local()

    @wraps(func)
    def wrapper(*args, **kwargs):
        params = tuple(args) + tuple(kwargs.items())

        if not hasattr(func._thread_locals, 'seen'):
            func._thread_locals.seen = list()
        if params in func._thread_locals.seen:
            seen = func._thread_locals.seen
            names = [args[0].name for args in seen]
            loop = names[names.index(params[0].name):]+[params[0].name]
            m = 'circular dependancy detected: '+str(loop)[1:-1]+", ..."
            raise RuntimeError(m)

        func._thread_locals.seen.append(params)
        try:
            res = func(*args, **kwargs)
        finally:
            seen = func._thread_locals.seen
            i = seen.index(params)
            seen.pop(i)

        return res

    return wrapper

@recursion_detector
def trace_change(trait, inst, trace=None):
    if not trace:
        trace = ChangeTrace()
    if hasattr(trait, 'listeners'):
        for l in trait.listeners.get(inst,[]):
            # if not l.updating[l.target()]:
            #     l.updating[l.target()] = True
                old = inst._trait_values[trait.name]
                change = {'name': trait.name,
                          'owner': inst,
                          'old': old}

                for c in l.changes:
                    if change == c:
                        break
                else:
                    l.changes.append(change)

                trace.include_listener(l)

                cls = l.target().__class__
                t = getattr(cls, l._name)

                trace_change(t, l.target(), trace)

    return trace

def find_trait(inst, name):
    if hasattr(inst.__class__, name):
        trait = getattr(inst.__class__, name)
        if not isinstance(trait, TraitType):
            raise TraitError("The target trait '%s' is "
                             "not a TraitType" % name)
    else:
        raise TraitError("The name '%s' is not a trait of %s"
                         " instances" % (target, dep_cls))
    return trait

@contextlib.contextmanager
def nested_notification_hold(*instances):
    if len(instances)!=0:
        with instances[0].hold_trait_notifications():
            with nested_notification_hold(*instances[1:]):
                yield
    else:
        yield


class ChangeTrace(object):

    def __init__(self):
        self.callbacks = []

    def include_listener(self, listener):
        if listener in self.callbacks:
            i = self.callbacks.index(listener)
            self.callbacks.pop(i)
        self.callbacks.append(listener)


def requires(name, needs):
    return RequiresHandler(name, needs)


class RequiresHandler(EventHandler):

    def __init__(self, name, needs, target=None):
        self._name = name
        self.needs = needs
        self.changes = []
        self.current_trace = None
        self.target = target
        self.updating = rdict()
        self.sources = rdict()
        if target:
            self.updating[target]=False

    def __getstate__(self):
        d = self.__dict__.copy()
        d['_last_trace'] = None
        return d

    def _init_call(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if hasattr(self, 'func'):
            s = super(RequiresHandler, self)
            return s.__call__(*args, **kwargs)
        else:
            self._init_call(*args)
        return self

    def _trigger_updates(self, change):
        name, owner = change['name'], change['owner']
        trace = trace_change(find_trait(owner, name), owner)
        targets = [l.target() for l in trace.callbacks if l.target is not None]
        with nested_notification_hold(*set(targets)):
            for listener in trace.callbacks:
                cls = listener.target().__class__
                target_trait = getattr(cls, listener._name)

                change_cache = {}
                for c in listener.changes:
                    n = c['name']
                    o = c['owner']
                    c['new'] = o._trait_values[n]
                    change_cache[n] = c

                values = {}
                for source, names in self.sources.items():
                    for n in names:
                        values[n] = getattr(source, n)

                value = listener(listener.target(), change_cache, values)
                setattr(listener.target(), listener._name, value)

                listener.updating[listener.target()] = False
                listener.changes = []

    def setup_requirement(self, source, names, target=None):
        if target:
            self.target = weakref(target)
        if not self.target():
            raise TraitError('No target instance '
                             'has been specified')

        if source in self.sources:
            self.sources[source].extend(names)
        else:
            self.sources[source] = list(names)
        source.observe(self._trigger_updates, names)
        
        for n in names:
            t = find_trait(source, n)
            if not hasattr(t, 'listeners'):
                t.listeners = rdict()
            if source not in t.listeners.keys():
                t.listeners[source] = []
            if self not in t.listeners[source]:
                t.listeners[source].append(self)

    def instance_init(self, inst):
        self.setup_requirement(inst, self.needs, inst)