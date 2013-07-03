from multipath.multipath import path
from multipath.paths import posix, windows, smb, rsync

## Posix

def test_uri_posix_abs():
    u = path('/usr/local/dir/file.txt')
    print(u)
    assert type(u) == posix.PosixPath

def test_uri_posix_rel():
    u = path('./dir/file.txt')
    print(u)
    assert type(u) == posix.PosixPath

def test_uri_posix_rel_2():
    u = path('dir/file.txt')
    print(u)
    assert type(u) == posix.PosixPath

## Windows

def test_uri_windows_abs():
    u = path(r'c:\stuff\file.txt')
    print(u)
    assert type(u) == windows.WindowsPath

def test_uri_windows_abs_fail():
    try:
        u = path(r'q:\stuff\file.txt')
    except:
        # Should throw exception since we (probably) are cd'd to q: drive 
        assert True
    else:
        assert False

def test_uri_windows_abs_2():
    u = path(r'C:/stuff/file.txt')
    print(u)
    assert type(u) == windows.WindowsPath

def test_uri_windows_abs_extended():
    u = path(r'\\?\C:\stuff\file.txt')
    print(u)
    assert type(u) == windows.WindowsPath

def test_uri_windows_rel():
    u = path(r'.\file.txt')
    print(u)
    assert type(u) == windows.WindowsPath

def test_uri_windows_rel_3():
    u = path(r'dir\file.txt')
    print(u)
    assert type(u) == windows.WindowsPath

def test_uri_windows_rel_extended():
    u = path(r'\\?\looooongdir\file.txt')
    print(u)
    assert type(u) == windows.WindowsPath

"""
This probably cant be unambiguously detected:
def test_uri_windows_rel_2():
    u = path(r'./somefolder/file.txt')
    print(u)
    assert type(u) == WindowsURI
"""

## SMB/UNC

def test_uri_smb():
    u = path(r'\\hostname\share\dirname\filename.txt')
    print(u)
    assert type(u) == smb.SmbPath

def test_uri_smb_extended():
    u = path(r'\\?\UNC\hostname\share\dirname\filename.txt')
    print(u)
    assert type(u) == smb.SmbPath

## Rsync

def test_uri_rsync_daemon():
    u = path('username@hostname::/x/y/z')
    print(u)
    assert type(u) == rsync.RsyncPath

def test_uri_rsync_p():
    u = path('rsync://username@hostname:/x/y/z')
    print(u)
    assert type(u) == rsync.RsyncPath

"""
def test_glob():
    g = glob('directory/*')
    print(g)
    assert 
    g = glob(r'directory\*')
    print(g)
    # TODO assert something 
"""

if __name__ == '__main__':
    import os, logging
    logging.basicConfig(level=logging.INFO)
    
    if os.name == 'posix':
        test_uri_posix_abs()
        test_uri_posix_rel()
        test_uri_posix_rel_2()
    else:
        print('Skipping Posix-only tests!')
    if os.name == 'nt':
        test_uri_windows_abs()
        test_uri_windows_abs_2()
        test_uri_windows_abs_extended()
        test_uri_windows_rel()
        # test_uri_windows_rel_2()
        test_uri_windows_rel_3()
        test_uri_windows_rel_extended()
        test_uri_smb()
        test_uri_smb_extended()
    else:
        print('Skipping Windows-only tests!')
    test_uri_rsync_daemon()
    test_uri_rsync_p()
    #test_glob()
