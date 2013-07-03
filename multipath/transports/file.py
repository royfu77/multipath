"""
File transport
"""
import shutil, os, re, logging, subprocess, string
from urllib import parse as urllib_parse 

log = logging.getLogger(__name__)

def copy(src, dest, copy_func=shutil.copy2, dir_exist_ok=True, os_username=None, os_password='', **kwargs):
    """
    local file transport
    File URIs in Windows: http://blogs.msdn.com/b/ie/archive/2006/12/06/file-uris-in-windows.aspx
    """
    log.debug('file transport: {} -> {} kwargs={}'.format(src, dest, kwargs))

    # TODO support ignoring files?
    """
    filenames_to_ignore = {}
    if ignore is not None: filenames_to_ignore = ignore(dirpath, filenames)
    for filename in filenames:
        if filename in filenames_to_ignore: continue
        # exists_ok is new in Python 3.2
        os.makedirs(dest_dirpath, exist_ok=exist_ok)
        fq_src_path = os.path.sep.join((dirpath, filename))
        fq_dest_path = os.path.sep.join((dest_dirpath, filename))
        copy_function(fq_src_path, fq_dest_path)
    """

    # Normalize paths
    if is_nt_path(src):
        src = src.replace('/', os.path.sep)
    if is_nt_path(dest):
        dest = dest.replace('/', os.path.sep)
            
    # Log on if Windows UNC
    if is_unc(src) and os_username:
        # Log user onto Windows server
        log.debug('Trying to log user %(os_username)s onto %(path)s' % dict(os_username=os_username, path=src))
        # Have to remove \\?\UNC from extended UNC paths or NET fails.
        # HACK net use fails if there is a trailing slash (\)
        cmd = 'NET USE ' + src.replace(r'\\?\UNC', '\\').rstrip('\\') + ' /User:' + os_username + ' ' + os_password
        log.debug('Excecuting: %(cmd)s' % dict(cmd=cmd))
        r = subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        log.debug("NET USE said: %s" % r)
    else:
        log.debug('Source is a UNC but no OS username has been provided.')
    if is_unc(dest) and os_username:
        # Log user onto Windows server
        log.debug('Trying to log user %(os_username)s onto %(path)s' % dict(os_username=os_username, path=dest))
        # Have to remove \\?\UNC from extended UNC paths or NET fails.
        # HACK net use fails if there is a trailing slash (\)
        cmd = 'NET USE ' + dest.replace(r'\\?\UNC', '\\').rstrip('\\') + ' /User:' + os_username + ' ' + os_password
        log.debug('Excecuting: %(cmd)s' % dict(cmd=cmd))
        r = subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        log.debug("NET USE said: %s" % r)
    else:
        log.debug('Destination is UNC path is a UNC but no OS username has been provided.')

    # On Windows, rewrite local paths to use extended file names
    if os.name == 'nt':
        src = to_extended(src)
        dest = to_extended(dest)

    # Possibly create destination directory
    # Creating dest dir only makes sense if src is not a file.
    if not os.path.isfile(src) and not os.path.exists(dest):
        os.makedirs(dest, exist_ok=dir_exist_ok)

    # List of destination file paths that were copied
    copied_to_dest = []

    if os.path.isfile(src) and os.path.isfile(dest):
        log.debug('Overwrite file dest with file src')
        copied_to_dest.append(copy_func(src, dest))
    elif os.path.isfile(src) and os.path.isdir(dest):
        log.debug('Copy file src into dir dest')
        copied_to_dest.append(copy_func(src, dest))
    elif os.path.isfile(src) and dest[-1] not in ['/','\\']:
        log.debug('Copy file to new file')
        os.makedirs(os.path.dirname(dest), exist_ok=dir_exist_ok)
        copied_to_dest.append(copy_func(src, dest))
    elif os.path.isfile(src) and dest[-1] in ['/','\\']:
        log.debug('Copy file to new file into new dir')
        os.makedirs(dest, exist_ok=dir_exist_ok)
        copied_to_dest.append(copy_func(src, dest))
    elif os.path.isdir(src) and src[-1] not in ['/','\\'] and os.path.isdir(dest):
        log.debug('Copy dir src into dir dest.')
        src_dir_basename = os.path.basename(src)
        dest_dir = os.path.join(dest, src_dir_basename)
        copied_to_dest += copytree(src, dest_dir)
    elif os.path.isdir(src) and src[-1] in ['/','\\'] and os.path.isdir(dest):
        log.debug('Recursively copy contents of dir src into dir dest')
        # Dest will be created. Will fail if dest exists
        copied_to_dest += copytree(src, dest)
    else:
        log.debug('Trying naive copytree')
        copied_to_dest += copytree(src, dest)

    log.debug('File transport copied {} files'.format(len(copied_to_dest)))
    return copied_to_dest

def list(source_root_dir, source_glob=None, target_root_dir=None, source_regex='.*', 
               source_changelog_path=None, start_rev=None, end_rev=None, source_statuses=None,
               regex_func='search'):
    """
    Arguments:
        source_glob: File glob. Should be relative to source_root_dir.
        source_root_dir: Root dir from which source_glob will be applied.
        target_root_dir (Optional): If provided, target (i.e. build) dir where target path names will be relative to.
    
    Returns: List of dicts
        source_path: Path to source file. Directories included depends on source_glob. 
        source_abs_path: Abolute version of source_path.
        source_root_dir: Same as argument source_root_dir. 
        source_root_abs_dir: Absolute version of source_root_dir.
        source_glob: Same as argument source_glob.
        no_root_path
        target_path (Optional): Path to target file. Directories included depends on source_glob. 
        target_abs_path (Optional): Absolute version of target_path
        target_root_dir (Optional): Same as argument target_root_dir
        target_root_abs_dir (Optional): Absolute version of target_root_abs_dir 
    """
    log.debug('Locals are: {}'.format(locals()))
    
    #source_root_dir = os.path.abspath(source_root_dir)
    #target_root_dir = os.path.abspath(target_root_dir)
    source_root_abs_dir = os.path.normpath(os.path.abspath(source_root_dir))
    
    filter_pattern = re.compile(source_regex)

    # Make a list of individual source file paths
    source_files = []
    
    found_files = []
    if source_glob:
        found_files = _list_files_glob(source_root_dir, source_glob)
    elif source_changelog_path:
        found_files = _list_files_changelog(source_changelog_path=source_changelog_path, start_rev=start_rev, end_rev=end_rev, 
                                            source_statuses=source_statuses, source_root_dir=source_root_dir)
    elif source_root_dir:
        found_files = _list_files_recurse_dir(source_root_dir)
    else:
        raise Exception('You must supply either a source glob, changelog path, or source root dir') 

    log.debug('File path generator returned {} files'.format(len(found_files)))

    for (source_path, change_status) in found_files:
        source_dict = dict()
        
        # Filter based on source_regex
        match = getattr(filter_pattern, regex_func)(source_path)
        if not match:
            log.debug('Skipping file {} because it didnt match regex {} with function {}'.format(source_path, source_regex, regex_func))
            continue
        log.debug('Found match: {}'.format(source_path))
        source_dict['match'] = match
        
        # Filter base on source_statuses / svn status from changelog
        if source_statuses and change_status not in source_statuses:
            log.debug('Skipping file {} because its change status {} is not in {}'.format(source_path, change_status, source_statuses))
            continue
        source_dict['change_status'] = change_status
        
        source_abs_path = os.path.normpath(os.path.abspath(source_path))
        source_rel_path = os.path.relpath(source_abs_path, start=source_root_abs_dir)
        
        # HACK backwards compatability. Refactor out.
        no_root_path = source_rel_path 
        
        source_dict.update(dict(source_path=source_path,
                            source_abs_path=source_abs_path, 
                            source_root_dir=source_root_dir,
                            source_root_abs_dir=source_root_abs_dir,
                            source_rel_path=source_rel_path,
                            source_glob=source_glob,
                            no_root_path=no_root_path) )
        
        # Optionally figure out what target params should be
        if target_root_dir:
            target_path = os.path.join(target_root_dir, source_rel_path)
            target_dict = dict(
                target_path=target_path,
                target_abs_path = os.path.abspath(target_path),
                target_root_dir=target_root_dir,
                target_root_abs_dir = os.path.abspath(target_root_dir)
                )
            source_dict.update(target_dict)
        
        log.debug('Source dict is: %s' % source_dict)
        
        source_files.append(source_dict)
    
    return source_files

def list(self, include=['.*'], exclude=[], visitors=[], recursive=True, **visitor_kwargs):
    """
    Arguments
    ---------
    include: regular expression(s) indicating which paths to include
    exclude: regular expression(s) indicating which paths to exclude. Overrides include.
    visitors: list of callables to apply to each path that will be returned.
    **visitor_kwargs: kwargs passed directly to visitors
    """
    include_patterns = []
    exclude_patterns = []
    
    log.debug('Include regexes: {}'.format(include))
    log.debug('Exclude regexes: {}'.format(exclude))
    
    if type(include) == str:
        include = [include]
    for include_regex in include:
        include_patterns.append(re.compile(include_regex))
    
    if type(exclude) == str:
        exclude = [exclude]
    for exclude_regex in exclude:
        exclude_patterns.append(re.compile(exclude_regex))
    
    if recursive:
        path_generator = os_walk_path_generator
    else:
        path_generator = os_listdir_path_generator
    
    for root in self.roots:
        # for dirpath, subdirs, filenames in os.walk(root):
        #    for filename in filenames:
        for path in path_generator(root):
            # abs_path = os.path.join(dirpath, filename)
            filename = os.path.basename(path)
            abs_path = os.path.abspath(path)
            rel_path = os.path.relpath(abs_path, start=root)
            abs_dirpath = os.path.dirname(abs_path)
            
            # Apply filter(s)
            if not include_patterns or not len(include_patterns) or len([True for p in include_patterns if p.match(rel_path)]):
                # An include regex matched relative path
                pass
            else:
                continue
            if len([True for p in exclude_patterns if p.match(rel_path)]):
                # An exclude regex matched relative path, so don't yield file
                continue
            
            file_dict = dict(root=root, filename=filename, abs_dirpath=abs_dirpath, abs_path=abs_path, rel_path=rel_path)
            
            # Possibly apply visitors
            for visitor in visitors:
                kwargs = dict()
                kwargs.update(file_dict)
                kwargs.update(visitor_kwargs)
                file_dict.update(visitor(**kwargs))
            
            yield file_dict

def glob(self, include=[], exclude=[], visitors=[], **visitor_kwargs):
    """
    Like list(), but supports globs instead of regular expressions.
    """
    log.debug('Include globs: {}'.format(include))
    log.debug('Exclude globs: {}'.format(exclude))
    
    include_regex = []
    exclude_regex = []

    fix_regex_pattern = re.compile(r'\.\*')
    if type(include) == str:
        include = [include]
    for g in include:
        g = os.path.normpath(g)
        glob_regex = fix_regex_pattern.sub(r'[\-\_\w]*?', fnmatch.translate(g))
        include_regex.append(glob_regex)
    
    if type(exclude) == str:
        exclude = [exclude]
        exclude_regex.append(fnmatch.translate(g))

    return self.list(include=include_regex, exclude=exclude_regex, 
                     visitors=visitors, **visitor_kwargs)

#
#
#

def copytree(src, dest, copy_func=copy_func):
    """Similar to shutil.copytree(), but will overwrite files"""
    log.debug('copytree: {} -> {}'.format(src, dest))
    copied_dest = []
    for dirpath, subdirs, files in os.walk(src):
        # Get path of source file relative to source root
        rel_dirpath = os.path.relpath(dirpath, src)
        if rel_dirpath == '.':
            rel_dirpath = ''
        os.makedirs(os.path.join(dest, rel_dirpath), exist_ok=dir_exist_ok)
        for f in files:
            src_file = os.path.normpath(os.path.join(src, rel_dirpath, f))
            dest_file = os.path.normpath(os.path.join(dest, rel_dirpath, f))
            log.debug(src_file + ' -> ' + dest_file)
            copied_dest.append(copy_func(src_file, dest_file))
    log.debug('copytree() copied {} files'.format(len(copied_dest)))
    return copied_dest

def os_walk_path_generator(root):
    """
    Yields recursive list of filenames
    """
    for dirpath, subdirs, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

def os_listdir_path_generator(root):
    """
    Yields non-recursive list of filenames
    """
    for path in os.listdir(path=root):
        yield path

def _list_files_recurse_dir(source_root_dir):
    paths = []
    for dirpath, subdirs, filenames in os.walk(source_root_dir):
        for fn in filenames:
            paths.append((os.path.normpath(os.path.join(source_root_dir, dirpath, fn)), 'A'))
    return paths

def _list_files_glob(source_root_dir, source_glob):
    """Returns a list of files matching source_glob"""
    log.debug('locals are: {}'.format(locals()))
    fg = os.path.join(source_root_dir, source_glob)
    # fg = os.path.normpath(fg)
    paths = []
    for source_path in glob.glob(fg):
        paths.append((os.path.normpath(source_path), 'A'))
    return paths

def abspath(self, rel_path):
    return os.path.abspath(os.path.join(self.roots_suffix, rel_path))

def normpath(self, path):
    return os.path.normpath(path)

def split(self, path):
    """
    Split a path into meaningful variables. Subclass must implement()
    Returns: dict. Keys and values are decided by implementing class
    """
    raise NotImplementedError('Path splitter not provided by subclass')

def join(self, path):
    """
    Creates path from split() output
    Returns: string
    """
    raise NotImplementedError('Path joiner not provided by subclass')
