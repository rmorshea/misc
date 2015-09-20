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
            m = 'Circular dependancy detected: '+str(loop)[1:-1]+" ..."
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

class ChangeTrace(object):

    def __init__(self):
        self.callbacks = []

    def include_listener(self, listener):
        if listener in self.callbacks:
            i = self.callbacks.index(listener)
            self.callbacks.pop(i)
        self.callbacks.append(listener)

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

@recursion_detector
def trace_change(trait, inst, trace=None):
    if not trace:
        trace = ChangeTrace()
    if hasattr(trait, 'listeners'):
        for l in trait.listeners.get(inst,[]):
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
            t.current_trace = trace

            trace_change(t, l.target(), trace)

    return trace

def trigger_updates(trace):
    for listener in trace.callbacks:
        cls = listener.target().__class__
        target_trait = getattr(cls, listener._name)

        if target_trait.current_trace is not trace:
            break

        for c in listener.changes:
            n = c['name']
            o = c['owner']
            c['new'] = o._trait_values[n]
        
        value = listener(listener.target(), *listener.changes)
        target_trait.super_set(listener.target(), value)
        target_trait.current_trace = None

        listener.changes = []

def _set_as_requirement(self, obj, value):
    trace = trace_change(self, obj)
    self.super_set(obj, value)
    trigger_updates(trace)

def new_requirement(trait):
    if not hasattr(trait, 'super_set'):
        trait.set = types.MethodType(_set_as_requirement, trait)
        trait.super_set = types.MethodType(trait.__class__.set, trait)
        trait.current_trace = None

class requires(object):
    def __getattr__(self, attr):
        return RequireHandler(attr)
requires = requires()

class RequireHandler(EventHandler):

    def __init__(self, name, target=None):
        self._name = name
        self.changes = list()
        try:
            t = weakref(target)
        except:
            t = target
        self.target = t

    def _init_call(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if hasattr(self, 'func'):
            s = super(RequireHandler, self)
            return s.__call__(*args, **kwargs)
        elif hasattr(self, 'sources'):
            self._init_call(*args)
        else:
            self.sources = args
        return self

    def setup_requirement(self, inst, names):
        if not self.target():
            raise TraitError('No target instance '
                             'has been specified')

        trait = find_trait(self.target(), self._name)
        new_requirement(trait)
        
        for n in names:
            t = find_trait(inst, n)
            if not hasattr(t, 'listeners'):
                t.listeners = rdict()
            if inst not in t.listeners.keys():
                t.listeners[inst] = []
            if self not in t.listeners[inst]:
                t.listeners[inst].append(self)
            if not hasattr(t, 'updating'):
                new_requirement(t)

    def instance_init(self, inst):
        self.target = weakref(inst)
        self.setup_requirement(inst, self.sources)