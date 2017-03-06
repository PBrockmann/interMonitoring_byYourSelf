#!/bin/bash

listfiles=(\
ATM_bils_global_ave.nc \
ATM_evap_global_ave.nc \
)

outputDir=output_$$
rm -rf $outputDir
mkdir -p $outputDir

for file in ${listfiles[*]} ; do
	variable=`echo ${file%%_ave.nc} | cut -d'_' -f 2-`
	echo "------------------"
	echo $file $variable
	echo pyferret -nodisplay -script monitoring_ex1.jnl $outputDir/${file%%.nc} $file ${variable}[l=@sbx:120]
	pyferret -nodisplay -script monitoring_ex1.jnl $outputDir/${file%%.nc} $file ${variable}[l=@sbx:120]
done

