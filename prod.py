#!/usr/bin/env python
 
#====================================================
# Author: Patrick Brockmann (LSCE)
#
# Usage: ./prod.py simuList.txt
#====================================================

import urllib
from bs4 import BeautifulSoup
import sys
import sys, os
from jinja2 import Environment, FileSystemLoader

#=============================================================
with open(sys.argv[1]) as f:
    simuList = f.readlines()
simuList = [x.strip() for x in simuList]

print simuList


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
outputDir = "interMonitoring_" + str(os.getpid())
print outputDir
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

#for file in filesInter:
for file in filesInter[0:4]:		# Only 4 first files for testing

	color = frameColors[file.split('_')[0]]

	cmd = "pyferret -batch " + outputDir + "/images/" + file.replace(".nc",".png") + " -script " + scriptFile + " " + file
	print cmd
	os.system(cmd)
	
	cmd = "convert " + outputDir + "/images/" + file.replace(".nc",".png") + " " + outputDir + "/images/" + file.replace(".nc",".gif")
	print cmd
	os.system(cmd)

	cmd = "convert -geometry 50%x50% -bordercolor '" + color + "' -border 15x15 " + outputDir + "/images/" + file.replace(".nc",".png") + " " + outputDir + "/images/" + file.replace(".nc",".jpg")
	print cmd
	os.system(cmd)

#=============================================================
simuNames = [ os.path.basename(simu) for simu in simuList ]
title = ' vs '.join(simuNames)
cmd = "monitoring01_createindex -t 'Inter-monitoring: " + title + "' " + outputDir;
print cmd
os.system(cmd)


