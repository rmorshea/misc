from traitlets import *


def requires(this, *uses):
    """Create a handler to set the value of ``this`` based on what it ``uses``

    The handler should return the value for the trait ``this``. Traits which
    have a requirement handler setup to view ``this`` will be called prior to
    normal change notifiers so that by the time they are, all requirements
    have been fulfilled and the state of the :class:`HasTraits` instance is
    consistant.
    """
    return RequiresHandler(this, uses, None, None)


class RequiresHandler(EventHandler):

    def __init__(self, this_name, uses_names, this_inst=None, uses_inst=None):
        self.this_name = this_name
        self.uses_names = uses_names
        # bound funcs define instances in instance_init
        if this_inst is not None and uses_inst is not None:
            self.setup_direct_path(this_inst, uses_inst)
        self.updating = False

    def setup_direct_path(self, this_inst, uses_inst):
        self.this_inst = this_inst

        if hasattr(uses_inst, '_requires_handlers'):
            d = uses_inst._requires_handlers
        else:
            d = {}
            uses_inst._requires_handlers = d
        for name in self.uses_names:
            if name in d:
                l = d[name]
            else:
                l = []
                d[name] = l
            if self not in l:
                l.append(self)

            uses_inst.observe(self._notify_change, self.uses_names, type='change')

    def _notify_change(self, change):
        if self.updating:
            n = change['name']
            inst = change['owner']
            if inst._trait_values[name] == change['new']:
                return
        self._follow_change(change)

    def _follow_change(self, change):
        if (hasattr(self.this_inst, '_requires_handlers') and \
            self.this_name in self.this_inst._requires_handlers):
            d = self.this_inst._requires_handlers
            listeners = d[self.this_name]
        else:
            listeners = None

        if listeners is None:
            raw = self.func(self.this_inst, change)
            setattr(self.this_inst, self.this_name, raw)
        else:
            with self.this_inst.hold_trait_notifications():
                old = getattr(self.this_inst, self.this_name)
                raw = self.func(self.this_inst, change)
                setattr(self.this_inst, self.this_name, raw)
                new = getattr(self.this_inst, self.this_name)

                for l in listeners:
                    l.updating = True
                    l._notify_change({'owner': self.this_inst,
                                      'name': self.this_name,
                                      'old': old, 'new': new,
                                      'type': change})
            for l in listeners:
                l.updating = False

    def instance_init(self, inst):
        self._setup_direct_path(inst, inst)
