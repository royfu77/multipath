from pprint import pprint
import pysvn
from multipath.paths import svn

def test_svn_list_1():
	svn_path = svn.SvnPath('http://svn.apache.org/repos/asf/subversion/trunk')
	paths = svn_path.list(recursive=False)
	for path in paths:
		pprint(path)

	paths = svn_path.list(recursive=False, include=['build'])
	for path in paths:
		pprint(path)

if __name__ == '__main__':
	test_svn_list_1()
