import os
_cwd = os.getcwd()
class FileStamp(object):
	def __init__(self, path):
		self.path = path
		self.modtime = os.stat(os.path.join(_cwd, path)).st_mtime
	
	def __str__(self):
		return "%s@%s" % (self.path, self.modtime)

	def __repr__(self):
		return "#<%s: %s>" % (self.__class__.__name__, self)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.path == other.path and self.modtime == other.modtime
		elif isinstance(other, str):
			return self.path == other
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __hash__(self):
		return hash(self.path)

	def __cmp__(self, other):
		if self.path != other.path:
			return cmp(self.path, other.path)
		return cmp(self.modtime, other.modtime)


