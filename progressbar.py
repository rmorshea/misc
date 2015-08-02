"""A pure python progressbar lifted from https://github.com/rmorshea/progressbar"""

import sys

class Progressbar(object):

    _clear = True

    _default = {'pre':'' if _clear_output else '\r',
                'left':"[", 'symbol':'=', 'right':']',
                'post':" %d%%"}

    def __init__(self, length=20, limit=None, **kwargs):
    	"""A progressbar implamented in pure python"""
        self._current = None
        self.limit = limit
        self.length = length
        traits = self._merge_styles(kwargs)
        for key,value in traits.items():
            setattr(self, key, value)
        self.form = self._make_form(length)

    def _merge_styles(self, kwargs):
        traits = self._default.copy()
        for key,value in kwargs.items():
            if key in traits:
                value = '' if value is None else str(value)
                traits[key] = value
            else:
                raise ValueError('style argument "%s"'
                                 ' not recognized'%key)
        return traits

    def _make_form(self, length):
        left = self.pre+self.left
        spaces = length*len(self.symbol)
        inner = "%-"+str(spaces)+"s"
        right = self.right+self.post
        return left+inner+right

    render = lambda self,*args: self.form%args

    def printout(self, value):
        percent = float(value)/(self.limit or 1)
        num = int(round(percent*self.length))
        if num!=self._current:
            if self._clear and _clear_output:
                _clear_output()
            bar = self.symbol*num
            prcnt = 100 if num==self.length else percent*100
            rendered = self.render(bar, prcnt)
            sys.stdout.write(rendered)
            sys.stdout.flush()
            self._current = num