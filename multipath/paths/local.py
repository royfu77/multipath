"""
Extends and enhances os.path
"""
import os, shutil, logging, string, re
from multipath.paths import path as base

log = logging.getLogger(__name__)

class LocalPath(base.Path):
    """
    Base for Posix, Windows and SMB/UNC paths.
    """
    
    def __init__(self, path, *args, **kwargs):
        # Decide on canonical path
        if os.path.isabs(path):
            self._path = path
            self._abs_path = path
            self._rel_path = os.path.relpath(path, start=os.path.curdir)
        else:
            self._abs_path = os.path.abspath(path)
            self._rel_path = path
        super().__init__(*args, path=self._abs_path, **kwargs)
    
    def list(self, 
        include=['.*'], exclude=[], visitors=[], recursive=True, 
        files=True, dirs=True,
        **visitor_kwargs):
        """
        TODO What if self.path is a file?

        Arguments
        ---------
        files: include files in list?
        dirs: include dirs in list?
        include: regular expression(s) indicating which paths to include
        exclude: regular expression(s) indicating which paths to exclude. Overrides include.
        visitors: list of callables to apply to each path that will be returned.
        **visitor_kwargs: kwargs passed directly to visitors
        """
        # Pull in defaults
        if visitors and not len(visitors):
            visitors = self.visitors
        log.debug('Visitors: {}'.format(visitors))

        (include_patterns, exclude_patterns) = base.compile_filters(include, exclude)
        """
        # Make lists of include and exclude patterns
        include_patterns = []
        exclude_patterns = []
        if type(include) == str:
            include = [include]
        for include_regex in include:
            # HACK Windows compatability
            include_regex = include_regex.replace('/', r'[\\/]')
            include_patterns.append(re.compile(include_regex))
        if type(exclude) == str:
            exclude = [exclude]
        for exclude_regex in exclude:
            # HACK Windows compatability
            exclude_regex = exclude_regex.replace('/', r'[\\/]')
            exclude_patterns.append(re.compile(exclude_regex))

        log.debug('Include regexes: {}'.format(include))
        log.debug('Exclude regexes: {}'.format(exclude))
        """

        # Decide which path generator to use        
        if os.path.isfile(self.path):
            path_generator = echo_path_generator
        elif recursive:
            path_generator = os_walk_path_generator
        else:
            path_generator = os_listdir_path_generator
        
        for path in path_generator(self.path, files=files, dirs=dirs):
            filename = os.path.basename(path)
            abs_path = os.path.abspath(path)
            rel_path = os.path.relpath(abs_path, start=self.path)
            abs_dirpath = os.path.dirname(abs_path)
            
            # Apply filter(s)
            if not base.accept_path(path, include_patterns, exclude_patterns):
                continue
            """
            if not include_patterns or not len(include_patterns) or len([True for p in include_patterns if p.search(rel_path)]):
                # An include regex matched relative path
                log.debug('Including path: {}'.format(path))
            else:
                # log.debug('Skipping path: {}'.format(path))
                continue
            if len([True for p in exclude_patterns if p.search(rel_path)]):
                # An exclude regex matched relative path, so don't yield file
                log.debug('Excluding path: {}'.format(path))
                continue
            """
            
            file_dict = path.Path(path=path, root=self, filename=filename, abs_dirpath=abs_dirpath, abs_path=abs_path, rel_path=rel_path)
            
            # Possibly apply visitors
            for visitor in visitors:
                kwargs = dict()
                kwargs.update(file_dict)
                kwargs.update(visitor_kwargs)
                file_dict.update(visitor(**kwargs))
            
            yield file_dict

    def copy(self, dest, metadata=True, copy_func=shutil.copy2, 
            include=['.*'], exclude=[], recursive=True,
            files=True, dirs=True,
            dir_exist_ok=False, dry_run=False,
            delete=False, mirror=False, 
            **kwargs):
        """
        Arguments:
            copy_func: Must follow same contract as shutil.copy(), i.e. "Returns the path to the newly created file."
            username:
            password:
            files: Copy files? If true, empty dirs will be copied.
            dirs: Copy dirs? If true, empty dirs will be copied. If false, empty dirs won't.
            dry_run: Don't actually copy. Just report via log.debug()
            All others, see path.Path
        Returns:
            list of tuples of source Path and destination Path
        """
        log.debug('Ignoring these keyword args: {}'.format(kwargs))

        # FIXME class should be same as calling sublcass?  
        """
        if not isinstance(dest, base.Path):
            dest = multipath.path(dest)
        """

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

        # List of destination file paths that were copied
        copied_to_dest = []

        paths_to_copy = self.list(include=include, exclude=exclude, recursive=recursive, files=files, dirs=dirs)
        for src in paths_to_copy:
            # FIXME class should be same as calling sublcass?
            # final_dest = multipath.path(join_consistently(dest.path, src.get('rel_path')))
            final_dest = LocalPath(join_consistently(dest.path, src.get('rel_path')))

            if dry_run:
                log.debug('Should copy {} to {}'.format(src.path, final_dest.path))
                continue

            # Possibly create destination directory
            # Creating dest dir only makes sense if src is not a file.
            if not os.path.isfile(src) and not os.path.exists(dest):
                os.makedirs(dest, exist_ok=dir_exist_ok)

            # Actually copy file
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
                # FIXME
                dest_dir = os.path.join(dest, src_dir_basename)
                copied_to_dest += copytree(src, dest_dir, copy_func=copy_func)
            elif os.path.isdir(src) and src[-1] in ['/','\\'] and os.path.isdir(dest):
                log.debug('Recursively copy contents of dir src into dir dest')
                # Dest will be created. Will fail if dest exists
                copied_to_dest += copytree(src, dest, copy_func=copy_func)
            else:
                log.debug('Trying naive copytree')
                copied_to_dest += copytree(src, dest, copy_func=copy_func)

            copied_to_dest.append((src, dest))

        log.debug('File multipath copied {} files'.format(len(copied_to_dest)))
        return copied_to_dest

## Path manipulation functions

def echo_path_generator(root, files=True, dirs=True):
    log.warn('Unused argument: files={}'.format(files))
    log.warn('Unused argument: dirs={}'.format(dirs))
    return [root]

def os_walk_path_generator(root, files=True, dirs=True):
    """
    Yields recursive list of filenames
    """
    log.debug('os_walk_path_generator(root={}, files={}, dirs={})'.format(root, files, dirs))
    # Special case where root is a file

    for dirpath, subdirs, filenames in os.walk(root):
        if files:
            for filename in filenames:
                yield os.path.join(dirpath, filename)
        if dirs:
            for subdir in subdirs:
                yield os.path.join(dirpath, subdir)

def os_listdir_path_generator(root, files=True, dirs=True):
    """
    Yields non-recursive list of filenames
    """
    log.warn('Unused argument: files={}'.format(files))
    log.warn('Unused argument: dirs={}'.format(dirs))
    for path in os.listdir(path=root):
        yield path

def join_consistently(*args):
    """Like os.path.join(), but examines path to decide which join char to use"""
    prejoined = "".join(args)
    sep = '/'
    if '/' not in prejoined and '\\' in prejoined:
        sep = '\\'
    return sep.join(args)

def copytree(src, dest, copy_func=shutil.copy2, dir_exist_ok=False):
    """
    Similar to shutil.copytree(), but will overwrite files.
    Arguments:
        src: Path object.
        dest: Path object.
    Returns: list of tuples of source, destination Path pairs.
    """
    log.debug('copytree: {} -> {}'.format(src, dest))
    copied_paths = []
    for dirpath, subdirs, files in os.walk(src.path):
        # Get path of source file relative to source root
        rel_dirpath = os.path.relpath(dirpath, src.path)
        if rel_dirpath == '.':
            rel_dirpath = ''
        os.makedirs(os.path.join(dest, rel_dirpath), exist_ok=dir_exist_ok)
        for f in files:
            src_file = os.path.normpath(os.path.join(src.path, rel_dirpath, f))
            dest_file = os.path.normpath(os.path.join(dest.path, rel_dirpath, f))
            log.debug(src_file + ' -> ' + dest_file)
            copied_paths.append(copy_func(src_file, dest_file))
    log.debug('copytree() copied {} files'.format(len(copied_paths)))
    return copied_paths

## Path information functions

def is_local(path):
    """True if path is on the local file system"""
    
    # TODO path.startswith('.') or path.startswith('/')
    
    return os.path.exists(path)


