from urllib import parse
from multipath.paths import path as base, local

class PosixPath(local.LocalPath):
	pass

def is_posix_path(path):
	return str(path).startswith('/') or str(path).startswith('./') or ( not parse.urlparse(str(path)).scheme and '/' in str(path) )
