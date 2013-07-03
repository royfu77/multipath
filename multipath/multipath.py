"""
Definitions
    path: raw path provided by user

References:
    Windows Paths: http://blogs.msdn.com/b/ie/archive/2006/12/06/file-Paths-in-windows.aspx
"""
import re, os, fnmatch
# FIXME only in python >= 3
from urllib import parse
# from urllib import parse
from multipath.paths import path as base, rsync, windows, smb, posix

def path(path, path_class=None):
    """
    Factory function for Path objects.
    """
    parsed_url = parse.urlparse(path)
    scheme = parsed_url.scheme

    if isinstance(path, base.Path):
        return path
    elif path_class:
        return path_class(path)
    elif smb.is_unc(path):
        return smb.SmbPath(path)
    elif windows.is_windows_path(path):
        return windows.WindowsPath(path)
    elif rsync.is_rsync_path(path):
        return rsync.RsyncPath(path)
    elif posix.is_posix_path(path):
        return posix.PosixPath(path)
    elif scheme == 'file':
        # FIXME decide on SmbPath, WindowsPath, PathPath, PosixPath, ...
        return posix.PosixPath(path)
    else:
        raise Exception('Cannot handle scheme {}'.format(scheme))
        # TODO Default to path? return PathPath(path)

def glob(pattern):
    """
    Turns a glob into a regex.
    """
    fix_regex_pattern = re.compile(r'\.\*')
    pattern = os.path.normpath(pattern)
    # HACK Windows compatability
    pattern = pattern.replace('/', r'[\\/]')
    glob_regex = fix_regex_pattern.sub(r'[\-\_\w]*?', fnmatch.translate(pattern))
    return glob_regex
