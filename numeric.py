class Variable(object):

    __val__ = None
    
    def __init__(self, v):
        """A mutable number"""
        self.__val__ = v

    # Comparison Methods
    def __eq__(self, x):
        return self.__val__ == x
    def __ne__(self, x):
        return self.__val__ != x
    def __lt__(self, x):
        return self.__val__ <  x
    def __gt__(self, x):
        return self.__val__ >  x
    def __le__(self, x):
        return self.__val__ <= x
    def __ge__(self, x):
        return self.__val__ >= x
    def __cmp__(self, x):
        if self.__val__ == x:
            return 0
        elif self.__val__ > 0:
            return 1
        return -1

    # Unary Ops
    def __pos__(self):
        return self.__class__(+self.__val__)
    def __neg__(self):
        return self.__class__(-self.__val__)
    def __abs__(self):
        return self.__class__(abs(self.__val__))

    # Bitwise Unary Ops
    def __invert__(self):
        return self.__class__(~self.__val__)

    # Arithmetic Binary Ops
    def __add__(self, x):
        return self.__class__(self.__val__ + x)
    def __sub__(self, x):
        return self.__class__(self.__val__ - x)
    def __mul__(self, x):
        return self.__class__(self.__val__ * x)
    def __div__(self, x):
        return self.__class__(self.__val__ / x)
    def __mod__(self, x):
        return self.__class__(self.__val__ % x)
    def __pow__(self, x):
        return self.__class__(self.__val__ ** x)
    def __floordiv__(self, x):
        return self.__class__(self.__val__ // x)
    def __divmod__(self, x):
        return self.__class__(divmod(self.__val__, x))
    def __truediv__(self, x):
        return self.__class__(self.__val__.__truediv__(x))

    # Reflected Arithmetic Binary Ops
    def __radd__(self, x):
        return self.__class__(x + self.__val__)
    def __rsub__(self, x):
        return self.__class__(x - self.__val__)
    def __rmul__(self, x):
        return self.__class__(x * self.__val__)
    def __rdiv__(self, x):
        return self.__class__(x / self.__val__)
    def __rmod__(self, x):
        return self.__class__(x % self.__val__)
    def __rpow__(self, x):
        return self.__class__(x ** self.__val__)
    def __rfloordiv__(self, x):
        return self.__class__(x // self.__val__)
    def __rdivmod__(self, x):
        return self.__class__(divmod(x, self.__val__))
    def __rtruediv__(self, x):
        return self.__class__(x.__truediv__(self.__val__))

    # Bitwise Binary Ops
    def __and__(self, x):
        return self.__class__(self.__val__ & x)
    def __or__(self, x):
        return self.__class__(self.__val__ | x)
    def __xor__(self, x):
        return self.__class__(self.__val__ ^ x)
    def __lshift__(self, x):
        return self.__class__(self.__val__ << x)
    def __rshift__(self, x):
        return self.__class__(self.__val__ >> x)

    # Reflected Bitwise Binary Ops
    def __rand__(self, x):
        return self.__class__(x & self.__val__)
    def __ror__(self, x):
        return self.__class__(x | self.__val__)
    def __rxor__(self, x):
        return self.__class__(x ^ self.__val__)
    def __rlshift__(self, x):
        return self.__class__(x << self.__val__)
    def __rrshift__(self, x):
        return self.__class__(x >> self.__val__)

    # Compound Assignment
    def __iadd__(self, x):
        self.__val__ += x; return self
    def __isub__(self, x):
        self.__val__ -= x; return self
    def __imul__(self, x):
        self.__val__ *= x; return self
    def __idiv__(self, x):
        self.__val__ /= x; return self
    def __imod__(self, x):
        self.__val__ %= x; return self
    def __ipow__(self, x):
        self.__val__ **= x; return self

    # Casts
    def __nonzero__(self):
        return self.__val__ != 0
    def __int__(self):
        return self.__val__.__int__()
    def __float__(self):
        return self.__val__.__float__()
    def __long__(self):
        return self.__val__.__long__()

    # Conversions
    def __oct__(self):
        return self.__val__.__oct__()
    def __hex__(self):
        return self.__val__.__hex__()
    def __str__(self):
        return self.__val__.__str__()

    # Random Ops
    def __index__(self):
        return self.__val__.__index__()
    def __trunc__(self):
        return self.__val__.__trunc__()
    def __coerce__(self, x):
        return self.__val__.__coerce__(x)

    # Represenation
    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.__val__)

    # Define innertype, a function that returns the type of the inner value self.__val__
    @property
    def innertype(self):
        return type(self.__val__)
    @innertype.setter
    def innertype(self, t):
        if t == self.innertype:
            return
        elif t is int:
            self.__val__ = self.__int__()
        elif t is float:
            self.__val__ = self.__float__()
        elif t is long:
            self.__val__ = self.__long__()
        else:
            TypeError("%s is not a numeric type"%str(t))

    # setter and getter for the varibale's value
    @property
    def value(self):
        return self.__val__
    @value.setter
    def setter(self, x):
        if   isinstance(x, (int, long, float)):
            self.__val__ = x
        elif isinstance(x, self.__class__):
            self.__val__ = x.__val__
        else:
            raise TypeError("%s is not a numeric type instance"%str(x))
        
    # Pass anything else along to self.__val__
    def __getattr__(self, attr):
        return getattr(self.__val__, attr)