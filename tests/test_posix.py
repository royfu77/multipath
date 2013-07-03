def test_uri_posix_abs():
    u = p('/usr/local/dir/file.txt')
    print(u)
    assert type(u) == PosixURI

def test_uri_posix_rel():
    u = p('./dir/file.txt')
    print(u)
    assert type(u) == PosixURI

def test_uri_posix_rel_2():
    u = p('dir/file.txt')
    print(u)
    assert type(u) == PosixURI