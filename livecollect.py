import os
import re
import sys
import gzip
import shutil
import xml.etree.ElementTree as ET

PATH_TYPE_MISSING 	= '0'
PATH_TYPE_EXTERNAL 	= '1'
PATH_TYPE_LIBRARY 	= '2'
PATH_TYPE_PROJECT 	= '3'

REL_SAMPLE_LOCATION = 'Samples/Imported/'
REGEX_PATTERN = r'^(\/.+\/)*((.+)\.(.+))$'

class Collector:

	SUPPORTED = [11]

	def __init__(self, path):
		self.fullPath	= path
		self.projPath = re.match(REGEX_PATTERN, path).group(1)
		self.fileName = re.match(REGEX_PATTERN, path).group(2)
		self.sampPath = self.projPath + REL_SAMPLE_LOCATION

		with gzip.open(path, 'r') as f:
			self.root	= ET.parse(f).getroot()
			f.close()

		self.version = int(self.root.attrib['MinorVersion'][:2])

		if self.version not in Collector.SUPPORTED:
			raise Exception(f'Live {self.version} is not supported by the collector')
	
	# Copy file to destination folder
	def copy_sample(self, src):
		os.makedirs(self.sampPath, exist_ok=True)
		shutil.copy2(src, self.sampPath)
	
	# Save current xml content to .als file
	def save_file(self):
		content = ET.tostring(self.root, encoding='utf8', method='xml')
		with gzip.open(self.fullPath, 'w') as f:
			f.write(content)
			f.close()

	def collect(self):
		filerefs = [r.find("FileRef") for r in self.root.iter('SampleRef')]

		if self.version == 11:
			for ref in filerefs:
				pathType = ref.find("RelativePathType")

				if pathType.attrib['Value'] == PATH_TYPE_EXTERNAL:
					
					truPath = ref.find("Path")
					relPath = ref.find("RelativePath")
					print(f'Copying external sample: {truPath.attrib["Value"]}')
					fileName = re.match(REGEX_PATTERN, truPath.attrib['Value']).group(2)

					self.copy_sample(truPath.attrib['Value'])
					print('Updating file references...')
					pathType.set('Value', PATH_TYPE_PROJECT)
					truPath.set('Value', self.sampPath + fileName)
					relPath.set('Value', REL_SAMPLE_LOCATION + fileName)

					print('Sample collected!')
			
			print('Saving to .als file...')
			self.save_file()
			print('Done!')
			
if __name__ == "__main__":
	name = sys.argv[1]
	coll = Collector(name)
	coll.collect()
