import re
import os
import subprocess
from numeric import Variable

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

	def help(self):
		print(self._help)

	def find(self):
		self.last_find = list(super(SearchReplace,self).find())
		return self.last_find

	def find_replacements(self, help=False, resume=True, force=False):
		"""mark identified instances for replacement

		For more info set 'help' to True"""
		if help:
			self.help()
		index = Variable(0)
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
			return self._handle_o(index,p,no,sub)
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

	def _handle_o(self, index, p, no, sub):
		cmd = 'sublime '+p+':'+str(no+1)+':1'
		try:
			subprocess.call(cmd.split(' '))
			custom = False
		except OSError, e:
			print('Sublime Text failed: '+e.__repr__())
			print("provide a *full* custom replacement (hit enter for none):\n")
			edit = raw_input('NEW ')
			custom = True
		if custom and edit is None:
			rawin = 'i'
		else:
			rawin = raw_input('command: ')
			if custom:
				sub = edit
		return self._handle_response(rawin,index,p,no,sub)

	def _handle_y(self, index, p, no, sub):
		self.replacements.append((p,no,sub))
		if self._index_dict.get(p,None):
			self._index_dict[p].append(index.value)
		else:
			self._index_dict[p] = [index.value]
		index += 1
		print('')

	def _handle_i(self, index, p, no):
		if not self.ignored.get(p,None):
			self.ignored[p] = [no]
		elif no not in self.ignored[p]:
			self.ignored[p].append(no)
		index += 1
		print('')

	def review_replacements(self):
		for rep in self.replacements:
			for last in self.last_find:
				if rep[0]==last[0] and rep[1]==last[1]:
					print('L'+str(rep[1])+' @ '+rep[0]+'\n'
						  'OLD '+last[2]+'NEW '+rep[2])

	def perform_replacements(self):
		if len(self.replacements)==0:
			raise AttributeError('nothing to replace')
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
			raise AttributeError('nothing to undo')
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