#!/usr/bin/env python

#====================================================
# Author: Patrick Brockmann (LSCE)
#
# Usage: ./prod_bokeh.py simuList.txt filesList.txt 12
#====================================================

import sys, os
import numpy as np
import netCDF4

#===========================================================
def sbx(array, windowsize):
    """
    Perform smoothing box 
    """
    
    w=int(windowsize/2.)
    b=np.ma.copy(array)
    l=len(array)
    for i in range(l) :
    		if i+1 <= w or i+1 > l-w :
    			b[i]=np.ma.masked
    		else :
    			ave=array[i-w:i+w+1]
    			b[i]=np.average(ave)
    
    return b

#===========================================================
def fnr(array, windowsize):
    """
    Perform fill nearest 
    """


#===========================================================
with open(sys.argv[1]) as f:
    simuList = f.readlines()
simuList = [x.strip() for x in simuList]

simuList = [ simu.replace('/thredds/catalog/', '/thredds/dodsC/') for simu in simuList ]

print simuList

#===========================================================
with open(sys.argv[2]) as f:
    filesList = f.readlines()
filesList = [x.strip() for x in filesList]

print filesList

#===========================================================
def readFile(file):

	f = netCDF4.Dataset(file)
	print f.variables.keys()
	varName = f.variables.keys()[-1]
	print varName

	values = f.variables[varName][...].squeeze()

	times= f.variables['TIME_COUNTER']
	timesUnits = times.units
	timesCalendar = times.calendar

	dates = np.asarray(netCDF4.num2date(times[:], units = timesUnits, calendar = timesCalendar), dtype=np.dtype('datetime64[us]'))

	f.close()

	return dates, values

#===========================================================
colors = [ "#3B63E6", "#FF4500", "#FFE000", "#34D314", "#FF1392", "#FFA400", 
	   "#775BB4", "#F5E6BD", "#789BF1", "#AFDFE6", "#0000C7", "#1FB1AA", 
	   "#B12121", "#DEB886", "#FFB6C1" ]

#===========================================================
from bokeh.io import output_file, show
from bokeh.layouts import gridplot
from bokeh.palettes import Viridis3
from bokeh.plotting import figure
from bokeh.models import Legend, ResizeTool

output_file("prod_bokeh.html")

smoothWindow = int(sys.argv[3])

ncols = 2
figArr = []
for i,file in enumerate(filesList):

	if i == 0:
		fig = figure(x_axis_type="datetime", title=file.replace('_ave.nc',''))
	else:
		fig = figure(x_axis_type="datetime", title=file.replace('_ave.nc',''), x_range=figArr[0].x_range)

	#fig.add_tools(ResizeTool())

	items = []
	for j,simu in enumerate(simuList):
		
		dates, values = readFile(simu + '/MONITORING/files/' + file)
		simuTag = os.path.basename(simu)
		p = fig.line(dates, sbx(values,smoothWindow), line_width=1, line_alpha=0.75, line_color=colors[j])
		items.append((simuTag, [p]))

	if i == 0:
		legend = Legend(items=items)	# Don't know how to add the legend with a gridplot

	figArr.append(fig)


grid = gridplot(figArr, ncols=ncols, plot_width=400, plot_height=400)

show(grid)

