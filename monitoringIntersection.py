#!/usr/bin/env python

#====================================================
# Author: Patrick Brockmann (LSCE)
#
# Usage: ./monitoringIntersection.py simuList.txt
#====================================================

import urllib
from bs4 import BeautifulSoup
import sys

with open(sys.argv[1]) as f:
    simuList = f.readlines()

simuList = [x.strip() for x in simuList]
print simuList 

setFiles = []
for i,simu in enumerate(simuList):

	print i, simu
	file = urllib.urlopen(simu + '/files/catalog.xml')
	handler = file.read()

	catalogSoup = BeautifulSoup(handler, "lxml")

	s = set()
	for tag in catalogSoup.findAll('dataset') :
		if tag['name'].endswith(".nc"):
			s.add(tag['name'])
	print len(s)
	setFiles.append(s)

filesInter = set.intersection(*setFiles)

print 
print len(filesInter)

for file in sorted(filesInter):
	print file
print

print("################################################################")
print("Missing files")
for i,s in enumerate(setFiles):
	print("\n%s" %(simuList[i]))
	for file in sorted(s):
		if file not in filesInter:
			print("    %s" %(file))
