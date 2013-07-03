import logging, os, re, string
from multipath.paths import path as base
from multipath.paths.local import LocalPath

log = logging.getLogger(__name__)

class WindowsPath(LocalPath):
    """
    Implements Windows (aka NT) paths as a Path.
    """
    def copy(self, *args, **kwargs):

        # TODO Normalize paths
        """
        if is_windows_path(self):
            src = str(self).replace('/', os.path.sep)
        if is_windows_path(dest):
            dest = dest.replace('/', os.path.sep)
        """
        
        # TODO On Windows, rewrite local paths to use extended file names
        """
        if os.name == 'nt':
            src = to_extended(src)
            dest = to_extended(dest)
        """
            
        super().copy(*args, **kwargs)

## Path identification functions

def is_windows_path(path):
    """Is this a Windows local path?"""
    return is_normal_path(path) or is_extended_path(path)

def is_normal_path(path):
    """Is this a normal, i.e. not extended, Windows path?"""
    return str(path)[1] == ':' or '\\' in str(path)

def is_extended_path(path):
    """Is this an extended Windows local path?"""
    return str(path).startswith(r'\\?') and not str(path).upper().startswith(r'\\?\UNC')

## Path manipulation functions

def to_extended(path):
    """Convert path to Windows extend file name"""
    # FIXME Make UNCs extended
    #if is_unc(path):
    #    path = path.replace('\\\\', '\\\\?\\UNC\\').replace('//', '//?/UNC/') 
    if str(path)[0] in string.ascii_lowercase + string.ascii_uppercase:
        path_str = '\\\\?\\' + str(path)
    return WindowsPath(path_str)
