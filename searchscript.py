import re
import os
import subprocess

class MutableNum(object):
	__val__ = None
	def __init__(self, v): self.__val__ = v
	# Comparison Methods
	def __eq__(self, x):        return self.__val__ == x
	def __ne__(self, x):        return self.__val__ != x
	def __lt__(self, x):        return self.__val__ <  x
	def __gt__(self, x):        return self.__val__ >  x
	def __le__(self, x):        return self.__val__ <= x
	def __ge__(self, x):        return self.__val__ >= x
	def __cmp__(self, x):       return 0 if self.__val__ == x else 1 if self.__val__ > 0 else -1
	# Unary Ops
	def __pos__(self):          return self.__class__(+self.__val__)
	def __neg__(self):          return self.__class__(-self.__val__)
	def __abs__(self):          return self.__class__(abs(self.__val__))
	# Bitwise Unary Ops
	def __invert__(self):       return self.__class__(~self.__val__)
	# Arithmetic Binary Ops
	def __add__(self, x):       return self.__class__(self.__val__ + x)
	def __sub__(self, x):       return self.__class__(self.__val__ - x)
	def __mul__(self, x):       return self.__class__(self.__val__ * x)
	def __div__(self, x):       return self.__class__(self.__val__ / x)
	def __mod__(self, x):       return self.__class__(self.__val__ % x)
	def __pow__(self, x):       return self.__class__(self.__val__ ** x)
	def __floordiv__(self, x):  return self.__class__(self.__val__ // x)
	def __divmod__(self, x):    return self.__class__(divmod(self.__val__, x))
	def __truediv__(self, x):   return self.__class__(self.__val__.__truediv__(x))
	# Reflected Arithmetic Binary Ops
	def __radd__(self, x):      return self.__class__(x + self.__val__)
	def __rsub__(self, x):      return self.__class__(x - self.__val__)
	def __rmul__(self, x):      return self.__class__(x * self.__val__)
	def __rdiv__(self, x):      return self.__class__(x / self.__val__)
	def __rmod__(self, x):      return self.__class__(x % self.__val__)
	def __rpow__(self, x):      return self.__class__(x ** self.__val__)
	def __rfloordiv__(self, x): return self.__class__(x // self.__val__)
	def __rdivmod__(self, x):   return self.__class__(divmod(x, self.__val__))
	def __rtruediv__(self, x):  return self.__class__(x.__truediv__(self.__val__))
	# Bitwise Binary Ops
	def __and__(self, x):       return self.__class__(self.__val__ & x)
	def __or__(self, x):        return self.__class__(self.__val__ | x)
	def __xor__(self, x):       return self.__class__(self.__val__ ^ x)
	def __lshift__(self, x):    return self.__class__(self.__val__ << x)
	def __rshift__(self, x):    return self.__class__(self.__val__ >> x)
	# Reflected Bitwise Binary Ops
	def __rand__(self, x):      return self.__class__(x & self.__val__)
	def __ror__(self, x):       return self.__class__(x | self.__val__)
	def __rxor__(self, x):      return self.__class__(x ^ self.__val__)
	def __rlshift__(self, x):   return self.__class__(x << self.__val__)
	def __rrshift__(self, x):   return self.__class__(x >> self.__val__)
	# Compound Assignment
	def __iadd__(self, x):      self.__val__ += x; return self
	def __isub__(self, x):      self.__val__ -= x; return self
	def __imul__(self, x):      self.__val__ *= x; return self
	def __idiv__(self, x):      self.__val__ /= x; return self
	def __imod__(self, x):      self.__val__ %= x; return self
	def __ipow__(self, x):      self.__val__ **= x; return self
	# Casts
	def __nonzero__(self):      return self.__val__ != 0
	def __int__(self):          return self.__val__.__int__()               # XXX
	def __float__(self):        return self.__val__.__float__()             # XXX
	def __long__(self):         return self.__val__.__long__()              # XXX
	# Conversions
	def __oct__(self):          return self.__val__.__oct__()               # XXX
	def __hex__(self):          return self.__val__.__hex__()               # XXX
	def __str__(self):          return self.__val__.__str__()               # XXX
	# Random Ops
	def __index__(self):        return self.__val__.__index__()             # XXX
	def __trunc__(self):        return self.__val__.__trunc__()             # XXX
	def __coerce__(self, x):    return self.__val__.__coerce__(x)
	# Represenation
	def __repr__(self):         return "%s(%d)" % (self.__class__.__name__, self.__val__)
	# Define innertype, a function that returns the type of the inner value self.__val__
	def innertype(self):        return type(self.__val__)
	# Define set, a function that you can use to set the value of the instance
	def set(self, x):
	    if   isinstance(x, (int, long, float)): self.__val__ = x
	    elif isinstance(x, self.__class__): self.__val__ = x.__val__
	    else: raise TypeError("expected a numeric type")
	# Pass anything else along to self.__val__
	def __getattr__(self, attr):
	    print("getattr: " + attr)
	    return getattr(self.__val__, attr)

class Search(object):

	def __init__(self, rootdir, pattern, filetype, context=None):
		self.files = list()
		self.rootdir = rootdir
		self.pattern = re.compile(r''+pattern)
		self.ftype = re.compile(r'.*(\.'+filetype+')$')
		match = self.ftype.match
		for root, sub, files in os.walk(rootdir):
			self.files += [(root,f) for f in files if match(f)]
		if not context or (isinstance(context,int) and context>0):
			self.context = context
		else:
			raise ValueError("'context' must be an int greater than zero or None.")

	def find(self):
		for root,name in self.files:
			path = os.path.join(root,name)
			with open(path, 'r') as f:
				lines = f.readlines()
				for i in range(len(lines)):
					if self.pattern.match(lines[i]):
						context = self.context
						if not context or context==0:
							yield (path,i,lines[i],('',''))
						else:
							if i-context<0:
								c1 = ''
								c2 = ''.join(lines[i+1:i+context+1])
							elif i+context+1>len(lines):
								c1 = ''.join(lines[i-context:i])
								c2 = ''
							else:
								c1 = ''.join(lines[i-context:i])
								c2 = ''.join(lines[i+1:i+context+1])
							yield (path,i,lines[i],(c1,c2))

	def as_dict(self):
		d = dict()
		for p,no,l,c in self.find():
			if d.get(p,None):
				d[p] = [(no,l,c)]
			elif (no,l,c) not in d[p]:
				d[p].append((no,l,c))

	def formated_find(self, with_context=False):
		for p,i,l,c in self.find():
			if with_context:
				out = ('L:'+str(i)+' @ '+p,''.join([c[0],l,c[1][:-1]]))
			else:
				out = ('L:'+str(i)+' @ '+p,l)
			yield out

class SearchReplace(Search):

	_help = ("-- HELP --\n"
			 "Confirmed replacements are appended to `self.replacements`, while the ignored\n"
			 "instances are appended to `self.ignored` and/or supressed in future replacement\n"
			 "searches. Quitted searches, or searches ended on an error, are resumable if\n"
			 "'resume' is True. To enact marked replacements call `self.perform_replacements()`.\n"
			 "\ty : mark a given instance for replacement.\n"
			 "\tn : ignore a given instance during replacement.\n"
			 "\ti : ignore an instance during replacement and future searches\n"
			 "\to : open the path at the given line in Sublime Text\n"
			 "\tq : quit the current replacement search.\n"
			 "\th : reprints this help text")

	def __init__(self, rootdir, filetype, pattern, repl_str=None, repl_func=None, context=None):
		super(SearchReplace,self).__init__(rootdir, pattern, filetype, context)
		self.replacements = list()
		self.ignored = dict()
		if not repl_str and not repl_func:
			raise ValueError("must provide either 'handle' or 'replament string'")
		elif repl_str and repl_func:
			raise ValueError("cannot provide both 'handle' and 'replament string'")
		self.repl_str = repl_str
		self.repl_func = repl_func
		# controls undo operation
		# (DO NOT EDIT CARELESSLY)
		self._index_dict = dict()
		self._on_quit_index = 0
		self.find()

	def help():
		print(self._help)

	def find(self):
		self.last_find = list(super(SearchReplace,self).find())
		return self.last_find

	def find_replacements(self, help=False, resume=True, force=False):
		"""mark identified instances for replacement

		For more info set 'help' to True"""
		if help:
			print(self._help)
		index = 0
		current_file = None
		if not resume:
			self._on_quit_index = 0
		if self._on_quit_index != 0:
			print('resuming replacement search...\n')
		for p,no,l,c in self.last_find[self._on_quit_index:]:
			if self.ignored.get(p,None) and no in self.ignored[p]:
				continue
			lno = 'L:'+str(no+1)
			print(lno+' @ '+p)
			if c==('',''):
				old = l[:-1]
			else:
				c1 = ('\n'+c[0][:-1]).replace('\n','\n....')
				c2 = ('\n'+c[1][:-1]).replace('\n','\n....')
				old = c1+'\n>>>>'+l[:-1]+c2+'\n'
			print(old)
			if self.repl_func:
				sub = self.repl_func(self.pattern, l)
			else:
				sub = self.pattern.sub(self.repl_str,l)
			print('NEW '+ sub)
			if force:
				self.replacements.append((p,no,sub))
				if self._index_dict.get(p,None):
					self._index_dict[p].append(index)
				else:
					self._index_dict[p] = [index]
				print('')
			else:
				rawin = raw_input('command: ')
				out = self._handle_response(rawin,index,p,no,sub)
				if out == 'quit':
					break

	def _handle_response(self,rawin,index,p,no,sub):
		if rawin == 'o':
			return self._handle_o(p,no,sub)
		elif rawin == 'y':
			self._handle_y(index,p,no,sub)
		elif rawin == 'q':
			self._on_quit_index = index
			return 'quit'
		elif rawin == 'i':
			self._handle_i(index,p,no)
		elif rawin == 'n':
			index += 1
			print('')
		elif rawin =='h':
			print(self._help)
			rawin = raw_input('command: ')
			return self._handle_response(rawin,index,p,no,sub)
		else:
			self._on_quit_index = index
			self.help()
			raise ValueError("must enter 'y','n','o','i','q', or 'h'")

	def _handle_o(self, p, no, sub):
		cmd = 'sublime '+p+':'+str(no+1)+':1'
		try:
			prompt = ''
			subprocess.call([cmd])
		except OSError, e:
			print('Sublime Text failed: '+e.__repr__())
			print("provide a *full* custom replacement (hit enter for none):\n")
			edit = raw_input('NEW ')
			if edit is not None:
				prompt = 'custom '
				sub = edit
		rawin = raw_input('confirm %sreplacement: \r' % prompt)
		return self._handle_response(rawin,index,p,no,sub)

	def _handle_y(self, index, p, no, sub):
		self.replacements.append((p,no,sub))
		if self._index_dict.get(p,None):
			self._index_dict[p].append(index)
		else:
			self._index_dict[p] = [index]
		index += 1
		print index
		print('')

	def _handle_i(self, index, p, no):
		if not self.ignored.get(p,None):
			self.ignored[p] = [no]
		elif no not in self.ignored[p]:
			self.ignored[p].append(no)
		index += 1
		print('')

	def perform_replacements(self):
		rawin = raw_input('execute all marked replacements (yes/no): ')
		if rawin == 'yes':
			repl_dict = dict()
			for p,no,sub in self.replacements:
				repls = repl_dict.get(p,None)
				if not repls:
					repl_dict[p] = [(no,sub)]
				else:
					repl_dict[p].append((no,sub))
			for p in repl_dict:
				with open(p, 'r') as f:
					lines = f.readlines()
				with open(p, 'w') as f:
					for lineno, repl in repl_dict[p]:
						lines[lineno] = repl
					f.writelines(lines)
		elif rawin == 'no':
			pass
		else:
			raise ValueError("must enter 'yes' or 'no'")

	def undo(self):
		if len(self.replacements)==0:
			print('nothing to undo')
			return
		rawin = raw_input('confirm revert (yes/no): ')
		if rawin == 'yes':
			for p in self._index_dict:
				with open(p, 'r') as f:
					lines = f.readlines()
				with open(p, 'w') as f:
					for index in self._index_dict[p]:
						entry = self.last_find[index]
						lines[entry[1]] = entry[2]
					f.writelines(lines)
		elif rawin == 'no':
			pass
		else:
			raise ValueError("must enter 'yes' or 'no'")

	def refresh(self):
		self.ignored = dict()
		self._on_quit_index = 0
		self.replacements = list()

	def formated_find(self, with_context=False):
		for p,i,l,c in self.last_find:
			if with_context:
				out = ('L:'+str(i)+' @ '+p,''.join([c[0],l,c[1][:-1]]))
			else:
				out = ('L:'+str(i)+' @ '+p,l)
			yield out