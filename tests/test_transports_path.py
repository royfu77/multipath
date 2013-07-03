import logging
from pprint import pprint
from multipath.paths import path as base

def test_path_list_1():
	p = base.Path('tests/fixtures')
	pprint(str(p))
	for uri in list(p.list()):
		pprint(str(uri))

def test_path_list_file():
	path_str = 'tests/fixtures/dir1/file2.txt'
	p = base.Path(path_str)
	pprint(str(p))
	for uri in list(p.list()):
		pprint(str(uri))
	assert path_str == list(p.list())[0].path

def test_path_list_exclude_dirs():
	p = base.Path('tests/fixtures')
	pprint(str(p))
	for uri in list(p.list(dirs=False)):
		pprint(str(uri))

def test_path_copy_1():
	src = base.Path('tests/fixtures')
	dest = base.Path('/tmp')
	src.copy(dest, dry_run=True)
	#for uri in list(p.copy(recursive=True, dry_run=False)):
	#	pprint(str(uri))	

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	print('test_path_list_1() ----------')
	test_path_list_1()
	print('test_path_list_file() ----------')
	test_path_list_file()
	print('test_path_list_exclude_dirs() ----------')
	test_path_list_exclude_dirs()
	print('test_path_copy_1() ----------')
	test_path_copy_1()
