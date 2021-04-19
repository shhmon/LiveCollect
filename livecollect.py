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

SUPPORTED = [11, 10]

class Collector:

	def __init__(self, path):
		self.liveSets = [f for f in os.listdir(path) if '.als' in f]
		self.projPath = path if path[-1] == '/' else (path + '/')
		self.sampPath = self.projPath + REL_SAMPLE_LOCATION

	def collect_project(self):
		for liveSet in self.liveSets:
			self.collect_live_set(liveSet)
	
	def collect_live_set(self, setName):
		setPath = self.projPath + setName
		# Open file and verify version
		with gzip.open(setPath, 'r') as f:
			root = ET.parse(f).getroot()
			f.close()

		version = int(root.attrib['MinorVersion'][:2])
		
		if version not in SUPPORTED:
			raise Exception(f'Live {version} is not supported by the collector')

		# Get all file references
		filerefs = [r.find("FileRef") for r in root.iter('SampleRef')]

		# Modify according to version
		for ref in filerefs:
			pathType = ref.find("RelativePathType")

			if pathType.attrib['Value'] == PATH_TYPE_EXTERNAL:

				if version == 11:
					truPath = ref.find("Path")
					relPath = ref.find("RelativePath")

					filePath = truPath.attrib["Value"]
					fileName = re.match(REGEX_PATTERN, filePath).group(2)

					# Update references
					truPath.set('Value', self.sampPath + fileName)
					relPath.set('Value', REL_SAMPLE_LOCATION + fileName)
	
				if version == 10:

					relPath = ref.find("RelativePath")

					# Construct path from relative path elements
					filePath = self.projPath[:-1]
					fileName = ref.find('Name').attrib['Value']
					relpElem = [e for e in relPath.iter('RelativePathElement')]

					for element in relpElem:
						value = element.attrib['Dir']
						filePath += '/' + (value if value else '..')
						relPath.remove(element)
					
					filePath += '/' + fileName

					# Update references
					ET.SubElement(relPath, 'RelativePathElement', attrib={'Dir': 'Samples', 'Id': str(len(relpElem)) })
					ET.SubElement(relPath, 'RelativePathElement', attrib={'Dir': 'Imported', 'Id': str(len(relpElem) + 1) })

					# Update the PathHint references (not sure if needed)
					pathHint = ref.find("SearchHint").find("PathHint")
					relpElem = [e for e in pathHint.iter('RelativePathElement')]

					for element in relpElem:
						pathHint.remove(element)

					dirList = self.projPath.split('/')[1:-1] + ['Samples', 'Imported']
					for i, _dir in enumerate(dirList):
						ET.SubElement(pathHint, 'RelativePathElement', attrib={'Dir': _dir, 'Id': str(len(relpElem) + i) })

			# Update path type
			pathType.set('Value', PATH_TYPE_PROJECT)

			# Copy the sample
			print(f'Copying external sample: {filePath}')
			self.copy_sample(filePath)

		# Save the live set		
		content = ET.tostring(root, encoding='utf8', method='xml')
		with gzip.open(setPath, 'w') as f:
			f.write(content)
			f.close()

		print('Done!')
			
	# Copy file to local sample folder
	def copy_sample(self, src):
		os.makedirs(self.sampPath, exist_ok=True)
		shutil.copy2(src, self.sampPath)
			
if __name__ == "__main__":
	name = sys.argv[1]
	coll = Collector(name)
	coll.collect_project()
