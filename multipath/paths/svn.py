"""
Path for SVN.
"""
import sys, logging, os
import pysvn
from multipath.paths import path as base

log = logging.getLogger(__name__)

class SvnPath(base.Path):
    def __init__(self, path, *args, **kwargs):
        self.client = pysvn.Client()
        if sys.version.startswith('2'):
            super(SvnPath, self).__init__(path=path, **kwargs)
        else:
            super().__init__(path=path, **kwargs)

    def list(self, 
            include=None, exclude=None, recursive=False, 
            visitors=None,
            # pysvn.list() only
            #peg_revision=pysvn.Revision( pysvn.opt_revision_kind.unspecified ),
            #revision=pysvn.Revision( pysvn.opt_revision_kind.head ),
            #dirent_fields=pysvn.SVN_DIRENT_ALL, # pysvn.dirent_fields
            #fetch_locks=False,
            # depth=None # depth is one of the pysvn.depth enums.
            **kwargs):

        peg_revision=None
        revision=None
        dirent_fields=None
        fetch_locks=False

        # TODO enable these commented arguments
        # pysvn.Client.list() "Returns a list with a tuple of information for each file in the given path at the provided revision."
        try:
            entries_list = self.client.list( self.path,
                    #peg_revision=peg_revision,
                    #revision=revision,
                    recurse=recursive)
                    #dirent_fields=dirent_fields,
                    #fetch_locks=fetch_locks )
                    #depth=depth )
        except Exception as e:
            log.error('Could not list SVN repository contents.')
            log.info('Possible solutions:')
            log.info('  - If behind a proxy, set environment variable')
            log.info('    HTTP_PROXY=http://USERNAME:PASSWORD@HOST:PORT')
            raise e
        # Compile filter patterns
        (include_patterns, exclude_patterns) = base.compile_filters(include, exclude)

        # Iterate over entries_list and apply include and exclude
        root_url = self.client.root_url_from_path( url_or_path=self.path )
        accepted_paths = []
        for (pysvn_list, pysvn_lock) in entries_list:

            abs_path = root_url + pysvn_list.repos_path
            # os.path.relpath seems to work on URLs
            rel_path = os.path.relpath(abs_path, start=root_url)

            path = SvnPath(abs_path)
            path['abs_path'] = abs_path
            path['rel_path'] = rel_path

            # SVN only
            path['repos_path'] = pysvn_list.repos_path

            # Apply filter(s)
            if base.accept_path(path, include_patterns, exclude_patterns):
                accepted_paths.append(path) 
        return accepted_paths
