"""
Windows Server Message Block. Paths are UNCs.
"""
from multipath.paths import path

class SmbPath(path.Path):
    def copy(self, dest, metadata=True,
            include=None, exclude=None, recursive=True,
            delete=False, mirror=False):

        # Normalize paths
        if is_nt_path(src):
            src = src.replace('/', os.path.sep)
        if is_nt_path(dest):
            dest = dest.replace('/', os.path.sep)

        # Log on if Windows UNC
        if is_unc(src) and username:
            # Log user onto Windows server
            log.debug('Trying to log user %(username)s onto %(path)s' % dict(username=username, path=src))
            # cmd = 'NET USE ' + norm_unc_for_net_use(src) + ' /User:' + username + ' ' + password
            cmd = net_use(src, username, password)
            log.debug('Excecuting: %(cmd)s' % dict(cmd=cmd))
            r = subprocess.check_call(cmd, stderr=subprocess.STDOUT)
            log.debug("NET USE said: %s" % r)
        else:
            log.debug('Source is a UNC but no OS username has been provided.')
        if is_unc(dest) and username:
            # Log user onto Windows server
            log.debug('Trying to log user %(username)s onto %(path)s' % dict(username=username, path=dest))
            # cmd = 'NET USE ' + norm_unc_for_net_use(dest) + ' /User:' + username + ' ' + password
            cmd = net_use(dest, username, password)
            log.debug('Excecuting: %(cmd)s' % dict(cmd=cmd))
            r = subprocess.check_call(cmd, stderr=subprocess.STDOUT)
            log.debug("NET USE said: %s" % r)
        else:
            log.debug('Destination is UNC path is a UNC but no OS username has been provided.')

        # On Windows, rewrite local paths to use extended file names
        if os.name == 'nt':
            src = to_extended(src)
            dest = to_extended(dest)

def net_use(unc, username, password=''):
    """Make a NET USE command"""
    if not password:
        password = ''
    cmd = 'NET USE ' + norm_unc_for_net_use(unc) + ' /User:' + username + ' ' + password
    return cmd

## Path identification functions

def is_unc(path):
    return is_normal_unc(path) or is_extended_unc(path)

def is_normal_unc(path):
    return not is_extended_unc(path) and path.startswith('\\\\') and not path.startswith(r'\\?')

def is_extended_unc(path):
    return path.startswith(r'\\?\UNC')

## Path manipulation functions

def norm_unc_for_net_use(unc):
    """Normalize a UNC so that it can be passed to NET USE command"""
    # Have to remove \\?\UNC from extended UNC paths or NET fails.
    unc = unc.replace(r'\\?\UNC', '\\')
    # net use fails if there is a trailing slash (\)
    unc = unc.rstrip('\\')
    # only keep \\server\share
    unc_split = unc.split('\\')
    unc = '\\\\' + unc_split[2] + '\\' + unc_split[3]
    return unc

def to_extended(path):
    """Convert path to Windows extend file name"""
    path = path.replace('\\\\', '\\\\?\\UNC\\').replace('//', '//?/UNC/') 
    return path 
