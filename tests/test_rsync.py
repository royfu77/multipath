from multipath.paths import rsync 

def test_rsync_1():
    src = rsync.RsyncPath(r'tests\fixtures\dirtree')
    dest = rsync.RsyncPath(r'rsync://hostname/tests/fixtures/dirtree')
    print(rsync.rsync(src, dest))

def test_rsync_2():
    src = rsync.RsyncPath(r'tests\fixtures\dirtree')
    dest = rsync.RsyncPath(r'rsync://hostname/tests/fixtures/dirtree')
    print(rsync.rsync(src, dest, mirror=True, f=True))

if __name__ == '__main__':
    test_rsync_1()
    test_rsync_2()