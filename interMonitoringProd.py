#!/usr/bin/env python
 
#====================================================
# Author: Patrick Brockmann (LSCE)
#
# Usage: ./prod.py simuList.txt
#====================================================

import sys, os, shutil
import urllib
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

#=============================================================
smooth = sys.argv[2] 

#=============================================================
dateOffset = []
simuList = []
for line in open(sys.argv[1]):
    li=line.strip()
    if len(li) != 0 and not li.startswith("#"):
        arr = line.rstrip().split('\t')
	arr = [x for x in arr if x != '']
	simuList.append(arr[0])
	if len(arr) > 1 :
		dateOffset.append(arr[1])
	else:
		dateOffset.append('""')

print simuList
print dateOffset

sys.exit()

#=============================================================
setFiles = []
for i,simu in enumerate(simuList):
        file = urllib.urlopen(simu + '/MONITORING/files/catalog.xml')
        handler = file.read()
        catalogSoup = BeautifulSoup(handler, "lxml")
        s = set()
        for tag in catalogSoup.findAll('dataset') :
                if tag['name'].endswith(".nc"):
                        s.add(tag['name'])
        setFiles.append(s)

filesInter = set.intersection(*setFiles)

if len(filesInter) == 0:
	sys.exit()

filesInter = sorted(filesInter)

#=============================================================
#outputDir = "interMonitoring_" + str(os.getpid())
outputDir = sys.argv[3]
print outputDir
shutil.rmtree(outputDir)
os.mkdir(outputDir)
os.mkdir(outputDir + "/images")

#=============================================================
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)

simuList = [ simu.replace('/thredds/catalog/', '/thredds/dodsC/') for simu in simuList ]

script = j2_env.get_template('interMonitoring.jnl.template').render(simuList=simuList)

scriptFile = outputDir + "/interMonitoring.jnl"
with open(scriptFile, "wb") as fh:
    fh.write(script)

#=============================================================
frameColors = {
	"ATM":	"#AECDFF", 
	"CHM":	"#F0D5F4", 
	"ICE":	"#D4E3E6", 
	"MBG":	"#D0F8E0", 
	"OCE":	"#6D80FF",
	"SBG":	"#EEE8AA",
	"SRF":	"#E7FFAB"
}

#=============================================================
quiet = " > /dev/null 2>&1"

#for file in filesInter:
for file in filesInter[20:24]:		# Only 4 first files for testing

	color = frameColors[file.split('_')[0]]

	cmd = "pyferret -noverify -quiet -batch " + outputDir + "/images/" + file.replace(".nc",".png") + " -script " + scriptFile + " " + file + \
			 " " + smooth + " " + ' '.join(dateOffset)
	print cmd
	os.system(cmd + quiet)
	
	cmd = "convert " + outputDir + "/images/" + file.replace(".nc",".png") + " " + outputDir + "/images/" + file.replace(".nc",".gif")
	print cmd
	os.system(cmd + quiet)

	cmd = "convert -geometry 50%x50% -bordercolor '" + color + "' -border 15x15 " + outputDir + "/images/" + file.replace(".nc",".png") + " " + \
			outputDir + "/images/" + file.replace(".nc",".jpg")
	print cmd
	os.system(cmd + quiet)

#=============================================================
simuNames = [ os.path.basename(simu) for simu in simuList ]
title = ' vs '.join(simuNames)
cmd = "monitoring01_createindex -t 'Inter-monitoring: " + title + "' " + outputDir;
print cmd
os.system(cmd)


