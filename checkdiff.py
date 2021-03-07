import difflib
import sys

# Usage: pyhton checkdiff.py file1.xml file2.xml

if __name__ == "__main__":
	(a, b) = sys.argv[1:3]
	file1 = open(a, "r").read().strip().splitlines()
	file2 = open(b, "r").read().strip().splitlines()
	
	for line in difflib.unified_diff(file1, file2, fromfile=a, tofile=b, lineterm=''):
		print(line)