"""
Rsync transport module
"""
import shutil, os, re, logging, subprocess, string
from urllib import parse as urllib_parse 

log = logging.getLogger(__name__)

def clean_rsync_local_path(path, os_name=os.name):
    if os_name == 'nt':
        (drive, rel_path) = os.path.splitdrive(path)
        if drive:
            rel_path = rel_path.lstrip('\\')
            path = '/'.join(('/cygdrive', drive[0], rel_path)).replace('\\', '/')
    return path

def make_rsync_cmd(src, dest, mirror=False, **kwargs):
    """Build rsync command line"""
    args = ['rsync']
    
    # Rewrite paths on windows to /cygdrive/ style. Needed by cwrsync.
    if os.name == 'nt':
        def _to_cygdrive(path):
            s = re.findall(r'([a-zA-Z]):\\(.*)', path)
            if len(s) and len(s[0]) == 2:
                path = '/cygdrive/{}/{}'.format(s[0][0], s[0][1])
            return path.replace('\\', '/') 
        src = _to_cygdrive(src)
        dest = _to_cygdrive(dest)
    
    for k, v in kwargs.items():
        # Meta arguments
        if mirror:
            args.append('-az')
            args.append('--delete')
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
    args.append(src)
    args.append(dest)
    return args

def copy(src, dest, recursive=True, makedirs=True, dir_exist_ok=True, mirror=False, **kwargs):
    """
    rsync transport
    
    Arguments:
        mirror: Runs rsync with `-az --delete` options.
    """
    log.debug('rsync transport: {} -> {} kwargs={}'.format(src, dest, kwargs))
    
    # TODO This will fail if dest is not on the local file system
    # Make destination dirs
    if makedirs:
        try:
            os.makedirs(dest, exist_ok=dir_exist_ok)
        except Exception as e:
            log.warn(e)

    def run_rsync(*args, **kwargs):
        """Execute rsync subprocess"""
        cmd = make_rsync_cmd(*args, **kwargs)
        r = subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        return r
    
    return run_rsync(src, dest, recursive=recursive, **kwargs)
