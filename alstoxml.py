
import sys
import xml.etree.ElementTree as ET
from gzip import GzipFile

def alstoxml(path):
	etree = ET.parse(GzipFile(path))
	etree.write('output.xml')

if __name__ == "__main__":
	path = sys.argv[1]
	alstoxml(path)