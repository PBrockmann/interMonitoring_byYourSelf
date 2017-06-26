#!/usr/bin/env python
 
#====================================================
# Author: Patrick Brockmann (LSCE)
#
# Usage: ./interMonitoringProdParallel.py simuList.txt
#====================================================

import sys, os, shutil
import urllib
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

from joblib import Parallel, delayed
import multiprocessing

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

print "################################################################################"
os.system("cat " + sys.argv[1])
print "################################################################################"
print simuList
print dateOffset
print "################################################################################"

#=============================================================
#outputDir = "interMonitoring_" + str(os.getpid())
outputDir = sys.argv[3]
shutil.rmtree(outputDir, ignore_errors=True)
os.mkdir(outputDir)
os.mkdir(outputDir + "/images")

shutil.copy(sys.argv[1], outputDir + "/simuList.txt")

print "Output directory: ", outputDir
print "################################################################################"

#=============================================================
num_cores = multiprocessing.cpu_count()
print "Number of processors: ", num_cores
print "################################################################################"

#=============================================================
simuListOk = []
setFiles = []
for i,simu in enumerate(simuList):
	print i+1, simu
	try:
        	file = urllib.urlopen(simu + '/MONITORING/files/catalog.xml')
        	handler = file.read()
        	catalogSoup = BeautifulSoup(handler, "lxml")
        	s = set()
        	for tag in catalogSoup.findAll('dataset') :
        	        if tag['name'].endswith(".nc"):
        	                s.add(tag['name'])
		print "--> Nb of monitoring files found: ", len(s) 
		if len(s) == 0:
			print "----> Zero length, will be skipped"
		else:
			simuListOk.append(simu)
        		setFiles.append(s)
	except:
		print "----> Read problem, will be skipped"
print "################################################################################"

filesInter = set.intersection(*setFiles)

for i,simu in enumerate(simuListOk):
	print simu
print "################################################################################"

filesInter = sorted(filesInter)

print 'Number of common files: ', len(filesInter)
print "################################################################################"

if len(filesInter) == 0:
	sys.exit()

#sys.exit()

#=============================================================
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)

simuListOk = [ simu.replace('/thredds/catalog/', '/thredds/dodsC/') for simu in simuListOk ]

script = j2_env.get_template('interMonitoring.jnl.template').render(simuList=simuListOk)

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

def processInput(file):
	color = frameColors[file.split('_')[0]]

	cmd = "pyferret -quiet -noverify -batch " + outputDir + "/images/" + file.replace(".nc",".png") + " -script " + scriptFile + " " + file + \
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

Parallel(n_jobs=num_cores)(delayed(processInput)(file) for file in filesInter)
#Parallel(n_jobs=num_cores)(delayed(processInput)(file) for file in filesInter[20:24])

#=============================================================
simuNames = [ os.path.basename(simu) for simu in simuListOk ]

title = 'Inter-monitoring: <ul style="font-size: 16px;">' + ''.join(['<li>' + s for s in simuNames]) + '</ul>'
cmd = "monitoring01_createindex -t '" + title + "' " + outputDir;
print cmd
os.system(cmd)

#=============================================================
print "################################################################################"
