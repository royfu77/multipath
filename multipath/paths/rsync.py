"""
"""
import os, logging, re, subprocess
from multipath.paths import path as base, cygwin

log = logging.getLogger(__name__)

hostname_regex = "(?!-)[A-Z\d-]{1,63}(?<!-)"

class RsyncPath(base.Path):
    """
    Implements rsync as a Path.
    """
    
    def __init__(self, path, **kwargs):
        # Decide on canonical path
        self._is_rsync_path = is_rsync_path(path)
        if not self._is_rsync_path and os.path.isabs(path):
            # This is not clearly an rsync path. Assume it's local
            self._path = path
            self._abs_path = path
            self._rel_path = os.path.relpath(path, start=os.path.curdir)
        elif not self._is_rsync_path and not os.path.isabs(path):
            self._abs_path = os.path.abspath(path)
            self._rel_path = path
        elif self._is_rsync_path:
            # Looks like a full rsync path
            self._path = path
            self._abs_path = path
        super().__init__(path=self._abs_path, **kwargs)
    
    def copy(self, dest, recursive=True, makedirs=True, dir_exist_ok=True, mirror=False, **kwargs):
        """
        Copy files via rsync.
        
        Arguments:
            mirror: Runs rsync with `-az --delete` options.
        """
        log.debug('rsync transport: {} -> {} kwargs={}'.format(self, dest, kwargs))
        
        # TODO This will fail if dest is not on the local file system
        # Make destination dirs
        if makedirs:
            # FIXME there's no exist_ok in python < 3
            try:
                os.makedirs(dest, exist_ok=dir_exist_ok)
            except Exception as e:
                log.warn(e)
            
        # Passing **kwargs leads to things like --os_username ending up on command line
        # return run_rsync(src, dest, recursive=recursive, **kwargs)
        return run_rsync(self, dest, recursive=recursive, mirror=mirror)

## Convenience functions

def rsync(src, dest, mirror=False, **kwargs):
    """Build rsync command line"""
    args = ['rsync']
    
    # Rewrite paths on windows to /cygdrive/ style. Needed by cwrsync.
    if os.name == 'nt':
        if not src._is_rsync_path:
            src = cygwin.to_cygdrive_path(src)
        if not dest._is_rsync_path:
            dest = cygwin.to_cygdrive_path(dest)

    # Meta arguments
    if mirror:
        args.append('-az')
        args.append('--delete')
    # Basic arguments
    for k, v in kwargs.items():
        # Real rync arguments 
        if type(v) == type(True):
            if v and len(k) == 1:
                args.append('-{}'.format(k))
            elif v:
                args.append('--' + k)
            else:
                args.append('--no-' + k)
        elif v and len(k) == 1:
            args.append('-{}'.format(k))
            args.append(v)
        elif v:
            args.append('--{}={}'.format(k, v))
        else:
            args.append('--{}'.format(k))
    args.append(src.abs_path)
    args.append(dest.abs_path)
    return args

def run_rsync(*args, **kwargs):
    """Execute rsync subprocess"""
    cmd = rsync(*args, **kwargs)
    r = subprocess.check_call(cmd, stderr=subprocess.STDOUT)
    return r

## Path information functions

def is_rsync_path(path):
    return is_rsync_uri(path) or is_rsync_shell(path) or is_rsync_daemon(path)

def is_rsync_uri(path):
    """Is this a Path style rsync path?"""
    return str(path).lower().startswith('rsync://')

def is_rsync_daemon(path):
    """
    Access via rsync daemon:
      Pull: rsync [OPTION...] [USER@]HOST::SRC... [DEST]
            rsync [OPTION...] rsync://[USER@]HOST[:PORT]/SRC... [DEST]
      Push: rsync [OPTION...] SRC... [USER@]HOST::DEST
            rsync [OPTION...] SRC... rsync://[USER@]HOST[:PORT]/DEST
    """
    if re.match('[a-zA-Z0-9]+@[a-zA-Z0-9\.]+::/.*', str(path)):
        return True
    elif re.match('[a-zA-Z0-9\.]+::/.*', str(path)):
        return True
    else:
        return False

def is_rsync_shell(path):
    if re.match('[a-zA-Z0-9]+@[a-zA-Z0-9\.]+:/.*', str(path)):
        # Access via remote shell with password
        return True
    elif re.match('[a-zA-Z0-9\.]+:/.*', str(path)):
        # Access via remote shell with no password
        return True
    else:
        return False



