multipath
=========

Multi-protocol high level path operations. Inspired by path.py and Unipath.

Plan
====

Multipath will work like this:

```python
>>> from multipath.multipath import path
>>> p = path('http://somehost/dir')
>>> p.list()
['http://somehost/dir/file1.html', 'http://somehost/dir/file2.html']
>>> src = path(r'c:\Users\user\file.txt')
>>> dest = path('rsync://hostname/user/')
>>> src.copy(dest)
```

Status
======

| module     | list | copy | delete | move | as_bytes | as_string | as_file |
| ---------- | -------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
| local      | | | | | | | |
| http       | | | | | | | |
| cygwin     | | | | | | | |
| windows    | | | | | | | |
| posix      | | | | | | | |
| smb        | | | | | | | |
