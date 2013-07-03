"""
Base for all Path implementations.
"""
import sys, logging, re

log = logging.getLogger(__name__)

class Path(dict):
    """
    Base class for all Path objects. 
    Don't instantate this class directly; call multipath.path() instead.
    """
    def __init__(self, path, **kwargs):
        self._init_path = path
        self._path = path
        if sys.version.startswith('2'):
            super(Path, self).__init__(path=path, **kwargs)
        else:
            super().__init__(path=path, **kwargs)

    def __str__(self):
        if self.abs_path:
            return self.abs_path
        else:
            return self.path
        
    def __repr__(self):
        return '{} {}'.format(type(self), self.path)

    # Properties
    
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, value):
        raise Exception('Path attributes are immutable')
    @path.deleter
    def path(self):
        raise Exception('Path attributes are immutable')
    
    @property
    def abs_path(self):
        return self._abs_path
    @abs_path.setter
    def abs_path(self, value):
        raise Exception('Path attributes are immutable')
    @abs_path.deleter
    def abs_path(self):
        raise Exception('Path attributes are immutable')

    @property
    def rel_path(self):
        return self._rel_path
    @rel_path.setter
    def rel_path(self, value):
        raise Exception('Path attributes are immutable')
    @rel_path.deleter
    def rel_path(self):
        raise Exception('Path attributes are immutable')
    
    # Functions that read or write

    def as_bytes(self):
        """
        Return contents of Path as bytes
        """
        raise NotImplementedError()

    def as_string(self, encoding='utf-8'):
        """
        Return contents of Path as string
        """
        raise NotImplementedError()

    def as_file(self, mode='r'):
        """
        Opens file object and returns file like object.
        """
        raise NotImplementedError()

    def delete(self, include=None, exclude=None, 
               recursive=False, force=False, dir=None):
        """
        Tries to combine functionality of shutil.rmtree(), os.rmdir(), os.remove(), os.removedirs(), os.unlink()
        Arguments:
            path: Object to remove. Can be file or directory.
            include: string or list of patterns to include. Can be glob or regex, depending on what
                implementing transport accepts.
            exclude: string or list of patterns to exclude. Can be glob or regex, depending on what
                implementing transport accepts.
            recursive: If true and path is directory, recursively delete all files and directories.
            force: Force removal of files when recursively deleting files.
        Meta-arguments:
            dir: Dir path to recursively delete. Sets recursive=True and force=True
        """
        raise NotImplementedError()

    # Functions that give information/metadata

    def list(self, 
            include=None, exclude=None, recursive=False, 
            visitors=None,
            **kwargs):
        """
        List files and directories. 

        Tries to combie os.listdir() and os.walk().
        Visitor functions can be applied to each path encountered in order to set additional
        info on the Path object returned.

        Arguments:
            include: string or list of patterns to include.
                Only used if path is a dir.
            exclude: string or list of patterns to exclude. 
                Only used if path is a dir.
            recursive: If true and path is a directory, lists all objects below path.
            visitors: Callables to apply to each object found. Visitors should return
                a dict.

        Returns: list of Path
        """
        raise NotImplementedError()

    def info(self, symlinks=True):
        """
        Like stat()

        Arguments
            symlinks: When false, behave like lstat()
        """
        raise NotImplementedError()

    # Functions that move files

    def copy(self, dest, metadata=True, dir_exist_ok=True,
            include=None, exclude=None, recursive=True,
            delete=False, mirror=False):
        """
        A full featured copy command. 
        Tries to combine best parts of rsync, shutil.copytree(), shutil.copy2()
        Arguments:
            dest: Path to copy to. Can be a Path object or string.
            metadata: if true, behave like shutil.copy2(), otherwise behave like shutil.copy()
            dir_exist_ok: if true, do not raise error when creating a directory that already exists.
            include: string or list of regex patterns to include.
                Only used if path is a dir.
            exclude: string or list of regex patterns to exclude. 
                Only used if path is a dir.
            recursive: if path is a directory, recursively copy all subfolders and files.
                Only used if path is a dir.
            delete: Deletes files in dest that arent in source.
                Only used if path is a dir.
        Meta-arguments:
            mirror: Makes copy behave like `rsync -az --delete`.
                Copies files from 
        """
        raise NotImplementedError() 

    def move(self, dest):
        raise NotImplementedError()

    def rename(self, dest):
        raise NotImplementedError()

## Convenience functions

def compile_filters(include=[], exclude=[]):
    """Compile regular expression strings into patterns via re.compile()"""
    include_patterns = []
    exclude_patterns = []
    
    # Make lists of include and exclude compiled regex patterns
    if include is None:
        include = []
    elif type(include) == str:
        include = [include]
    for include_regex in include:
        # HACK Windows compatability
        include_regex = include_regex.replace('/', r'[\\/]')
        include_patterns.append(re.compile(include_regex))
    if exclude is None:
        exclude = []
    elif type(exclude) == str:
        exclude = [exclude]
    for exclude_regex in exclude:
        # HACK Windows compatability
        exclude_regex = exclude_regex.replace('/', r'[\\/]')
        exclude_patterns.append(re.compile(exclude_regex))

    log.debug('Include regexes: {}'.format(include))
    log.debug('Exclude regexes: {}'.format(exclude))

    return (include_patterns, exclude_patterns)

def accept_path(path, include_patterns=None, exclude_patterns=None):
    """Filter a single path based on include and exclude pattern/filters"""
    is_accepted = True
    # Apply filter(s)
    if not include_patterns or not len(include_patterns) or len([True for p in include_patterns if p.search(path['rel_path'])]):
        # An include regex matched relative path
        log.debug('Including path: {}'.format(path))
        is_accepted = True
    else:
        # log.debug('Skipping path: {}'.format(path))
        return False # Shortcut; dont examine exclude pattern
    if len([True for p in exclude_patterns if p.search(path['rel_path'])]):
        # An exclude regex matched relative path, so don't yield file
        log.debug('Excluding path: {}'.format(path))
        return False # Shortcut
    return is_accepted

def reject_path(*args, **kwargs):
    return not accept_path(*args, **kwargs)

def ensure_string(path):
    if isinstance(path, str):
        return path
    else:
        return path.path
