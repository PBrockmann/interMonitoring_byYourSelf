#!/bin/bash

listfiles=(\
ATM_bils_global_ave.nc \
ICE_icevol_north_MAR_ave.nc \
ATM_evap_global_ave.nc \
)

outputDir=output_$$
rm -rf $outputDir
mkdir -p $outputDir

for file in ${listfiles[*]} ; do

	variable=`echo ${file%%_ave.nc} | cut -d'_' -f 2-`
	echo "------------------"
	echo $file $variable

	monthFromFile=`echo $file | awk -F_ '{print $(NF-1)}'`
	case $monthFromFile in
		JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)	transf="l=@FNR";;
   		 *)            						transf="l=@SBX:120";; 
	esac

	echo pyferret -nodisplay -script monitoring_ex1.jnl $outputDir/${file%%.nc} $file ${variable}[${transf}]
	pyferret -nodisplay -script monitoring_ex1.jnl $outputDir/${file%%.nc} $file ${variable}[${transf}]

done

