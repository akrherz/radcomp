#!/bin/bash

export YYYY="$1"
export YY="`echo $1 | cut -c 3-4`"
export MM="$2"
export DD="$3"
export HH="$4"
export MI="$5"
export JOB="$6"
export PROD="$7"

source /usr/local/nawips/Gemenviron.profile
export RAD=/home/ldm/data/nexrad/

nex2img << EOF > logs/nex2gini_${PROD}.log
 GRDAREA  = 24.01;-126.00;50.00;-66.01
 PROJ     = CED
 KXKY     = 12000;5200
 CPYFIL   =  
 GFUNC    = ${PROD}
 RADTIM   = ${YY}${MM}${DD}/${HH}${MI}
 RADDUR   = 15
 RADFRQ   =
 STNFIL   = nexrad.tbl
 RADMODE  = PC
 RADFIL   = ${PROD}_${JOB}.gif
 LUTFIL   = iem_lut256.tbl
 list
 run

 exit
EOF

rm -f ${PROD}_LOCK_${JOB}
