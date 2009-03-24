#!/bin/csh
# Script to create simple raster by gridding!
# Daryl Herzmann 4 Jul 2003
# 17 Jul 2003: Now we have nex2img!  Thanks Steve
# 25 Jul 2003: Now we are running this on kcci.mesonet, which rocks....

source /mesonet/nawips/Gemenviron
setenv RAD /mesonet/data/nexrad/
setenv PATH "${PATH}:/home/ldm/bin:/mesonet/local/bin"

set ftime="$1$2$3$4$5"
set gtime=`date -u +'%y%m%d/%H%M'`
set rad="$6"

if ($rad == "DMX") then
  set area = "38.72;-96.72;44.72;-90.72"
else if ($rad == "ABR") then
  set area = "42.45;-101.40;48.45;-95.40"
else if ($rad == "UDX") then
  set area = "41.12;-105.82;47.12;-99.82"
else if ($rad == "MPX") then
  set area = "41.83;-96.55;47.83;-90.55"
else if ($rad == "FSD") then
  set area = "40.58;-99.72;46.58;-93.72"
else if ($rad == "ARX") then
  set area = "40.82;-94.18;46.82;-88.18"
else if ($rad == "DVN") then
  set area = "38.60;-93.57;44.60;-87.57"
else if ($rad == "OAX") then
  set area = "38.32;-99.37;44.32;-93.37"
else if ($rad == "EAX") then
  set area = "35.80;-97.25;41.80;-91.25"
endif

nex2img << EOF > logs/nex2img_single_${rad}.log
 GRDAREA  = $area
 PROJ     = CED
 KXKY     = 600;600
 CPYFIL   =  
 GFUNC    = n0r
 RADTIM   = ${gtime}
 RADDUR   = 15
 RADFRQ   = 
 STNFIL   = tables/${rad}.stns
 RADMODE  = PC
 RADFIL   = radar.gif
 LUTFIL   = iem_n0r.tbl
 list
 run

 exit
EOF


if (-e radar.gif) then
  echo "${rad} ${ftime}" > tmp/${rad}.ts
  pqinsert -p "GIS_${ftime}_${rad}_N0R_4326.ts" tmp/${rad}.ts
  cp tables/${rad}.wld radar.wld
  gdal_translate -of GTiff radar.gif test.tif >& /dev/null
  compress test.tif
  pqinsert -p "gis r ${ftime} gis/images/4326/${rad}/n0r_ bogus tif.Z" test.tif.Z >& /dev/null
endif

rm radar.gif radar.wld test.tif* >& /dev/null
