from multipath.paths import path as base

def test_path_str():
	p = base.Path('/dir/path/file.txt')
	p._abs_path = '/dir/path/file.txt'
	print(str(p))

def test_path_repr():
	p = base.Path('/dir/path/file.txt')
	p._abs_path = '/dir/path/file.txt'
	print(repr(p))

if __name__ == '__main__':
	test_path_str()
	test_path_repr()


"""
>>> merge('/srcdir/file', '/destdir/')
/destdir/file
>>> merge('/srcdir/file', '/doesnt_exist_dir/')
/doesnt_exist_dir/file
>>> merge('/srcdir/file', '/destdir/file')
/destdir/file
>>> merge('/srcdir/subdir', '/destdir')
/destdir/subdir/{recursive contents of subdir}
>>> merge('/srcdir/subdir/', '/destdir/')
/destdir/{recursive contents of subdir}
>>> merge('./srcdir/subdir/', '/destdir')
/destdir/subdir/{recursive contents of subdir}
>>> merge('./srcdir/subdir/', 'destdir')
./destdir/subdir/{recursive contents of subdir}
>>> merge('user@ssh_rsync_server:/srcdir', '/destdir', recursive=True)
/destdir/subdir/{recursive contents of subdir}
>>> merge('ssh_rsync_server:/srcdir', '/destdir', recursive=True)
/destdir/subdir/{recursive contents of subdir}    
>>> merge('\\\\?\\UNC\\hostname\\share\\subdir', r'c:\\destdir')
c:\\destdir\\subdir\\{recursive contents of subdir}

# TODO:
>>> merge('/srcdir/subdir', '/destdir', transport=rsync_transport, recursive=True)
/destdir/subdir/{recursive contents of subdir}
>>> merge('./srcdir/subdir', '/destdir', transport=rsync_transport, recursive=True)
/destdir/subdir/{recursive contents of subdir}
# TODO Hacking the rsync src and dest strings:
>>> merge('rsync:///srcdir/subdir', '/destdir', recursive=True)
/destdir/subdir/{recursive contents of subdir}
>>> merge('rsync://./srcdir/subdir', '/destdir', recursive=True)
/destdir/subdir/{recursive contents of subdir}
# TODO Windows UNC:
>>> merge(r'//hostname/share/subdir', r'c:/destdir')
c:/destdir/subdir/{recursive contents of subdir}
>>> merge(r'//?/UNC/hostname/share/subdir', r'c:/destdir')
c:/destdir/subdir/{recursive contents of subdir}
"""