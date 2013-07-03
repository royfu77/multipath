"""
Special support for Cygwin paths.
"""
import os, re
from multipath.paths import posix

class CygwinPath(posix.PosixPath):
    """
    Inherits from PosixPath because, even though it runs on Windows, Cygwin uses Posix-style paths.
    """
    pass

def to_cygdrive_path(path):
    
    # FIXME On Windows, 'rsync://hostname/tests/fixtures/dirtree' becomes 'c:\\dev\\multipath\\rsync:\\hostname\\tests\\fixtures\\dirtree'
    
    """Convert a (probably Windows) path to a Cygwin `/cygdrive/X/...` path."""
    #if not os.path.isabs(path):
    #    path = os.path.abspath(path)
    s = re.findall(r'([a-zA-Z]):\\(.*)', path.abs_path)
    if len(s) and len(s[0]) == 2:
        path_str = '/cygdrive/{}/{}'.format(s[0][0], s[0][1])
    else:
        path_str = str(path)
    path_str = path_str.replace('\\', '/')
    return CygwinPath(path_str)