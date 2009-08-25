import nosexml
import cgi
import collections
import pickle
import base64

EOF = '__EOF__'

class Node(object):
	def __init__(self, parent, name, attrs={}):
		self.parent = parent
		self.name = name
		self.attrs = attrs
		self.children = []
		self.content = ''

	def push(self, name, attrs):
		node = type(self)(self, name, attrs)
		self.children.append(node)
		return node
	
	def add_content(self, content):
		self.content += content
	
	def __getitem__(self, name):
		try:
			return self.attrs[name]
		except KeyError:
			print "WARNING: node has no key %r - discarding." % (name,)
	
	def __repr__(self):
		return '<%s: (%r) children=(%r)>\n' % (self.name, self.attrs, self.children)

class Data(object):
	"""
	The least xml-like xmlFormatter plugin you'll ever see.
	instead of xml, it just writes root-level elements to a stream
	one line at a time as base64(pickle(node))
	
	Data.decode() is responsible for reversing this process on
	the other side of the stream.
	"""
	realStream = None
	
	def __new__(cls, *a, **kw):
		if getattr(cls, 'singleton', None) is None:
			cls.singleton = super(Data, cls).__new__(cls, *a, **kw)
			cls.__init__(cls.singleton, *a, **kw)
			cls.__init__ = lambda *a, **k: None
		return cls.singleton

	def __init__(self, stream):
		self.stream = self.realStream or stream
		self.depth = 0
		self.root = Node(None, 'root')
		self.current = self.root
	
	def startDocument(self):
		assert self.current is self.root, "Elements written before document started"
		self.startElement('new_run')
		self.endElement()

	def endDocument(self):
		assert self.current is self.root, "Not all elements were closed."

	def startElement(self, name, attrs={}):
		self.current = self.current.push(name, attrs)

	def endElement(self, name=None):
		parent = self.current.parent
		if parent is self.root:
			self._write_line(self.encode(self.current))
		self.current = parent
	
	def _write_line(self, line):
		try:
			self.stream.write(line)
			self.stream.write('\n')
			self.stream.flush()
		except IOError, e:
			# we can't be sure that sys.stdout/stderr work
			# at all, so we'll just write to a darn file
			import sys, subprocess, os, traceback
			error_file = open("/tmp/autonose-error","w")
			traceback.print_exc(file=error_file)
			error_file.write("\n")
			error_file.write("Note: this is the RUNNER pid (%s)\n" % (os.getpid(),))
			error_file.write("sys.stdout = %r\n" % (sys.stdout,))
			error_file.write("sys.stderr = %r\n" % (sys.stderr,))
			error_file.write("my (output) pipe = %r\n" % (self.stream,))
			error_file.write("realstream = %r\n" % (self.realStream,))
			error_file.write("UI PID = %s\n" % (type(self).ui_pid,))
			psout = subprocess.Popen(["ps"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
			#psout = "\n".join([l for l in psout.splitlines() if str(type(self).ui_pid) in l])
			error_file.write("PS output:\n%s\n" % (psout))

			error_file.close()
			raise


	def characters(self,content):
		if content:
			self.current.add_content(content)

	def encode(self, elem):
		pickled = pickle.dumps(elem)
		encoded = base64.encodestring(pickled)
		# ensure no whitespace in the content (base64 does this for readability)
		encoded_single_line = ''.join(encoded.split())
		return encoded_single_line + '\n'
	
	@staticmethod
	def decode(encoded):
		decoded = base64.decodestring(encoded)
		return pickle.loads(decoded + '\n')

