#!/bin/csh

source /mesonet/nawips/Gemenviron

setenv RAD /tmp/nexrad/

set yy="`echo $1 | cut -c 3-4`"
set gtime="$yy$2$3/$4$5"
set ftime="$1$2$3$4$5"

set lut="iem_n0r.tbl"
set radmode="PC"
set routes="a"
set routes2="o"
set routes3="o"
set fp="radar_$$.gif"

nex2img << EOF > /tmp/nex2gini_n0r.log
 GRDAREA  = 24.02;-126.00;50.00;-66.02
 PROJ     = CED
 KXKY     = 6000;2600
 CPYFIL   =  
 GFUNC    = N0R
 RADTIM   = ${gtime}
 RADDUR   = 15
 RADFRQ   =
 STNFIL   = nexrad.tbl
 RADMODE  = ${radmode}
 RADFIL   = ${fp}
 LUTFIL   = ${lut}
 list
 run

 exit
EOF


# Convert it to TIF for algorithm work
magick -compress none $fp n0r_$$_in.tif
rm -f $fp

# Now generate NET

nex2img << EOF > /tmp/nex2gini_net.log
 GRDAREA  = 24.02;-126.00;50.00;-66.02
 PROJ     = CED
 KXKY     = 6000;2600
 CPYFIL   =
 GFUNC    = NET
 RADTIM   = ${gtime}
 RADDUR   = 25
 RADFRQ   =
 STNFIL   = nexrad.tbl
 RADMODE  = ${radmode}
 RADFIL   = ${fp}
 LUTFIL   = upc_net.tbl
 list
 run


 exit
EOF


if ($2 == "01" || $2 == "02" || $2 == "03" || $2 == "04" ||  $2 == "10" || $2 == "11" || $2 == "12") then
	# Convert it to TIF for algorithm work
	magick -compress none $fp net_$$_in.tif
	

	python gdal-clean.py $$ $1$2$3$4$5

	# Lets finish up, finally
	magick -depth 8 n0r_$$_out.tif test_$$.png
else
	magick $fp test_$$.png
endif
rm -f $fp
/home/ldm/bin/pqinsert  -p "gis ${routes} ${ftime} gis/images/4326/USCOMP/n0r_ GIS/uscomp/n0r_${ftime}.png png" test_$$.png

python gentfw.py ${ftime} n0r
/home/ldm/bin/pqinsert  -p "gis a ${ftime} bogus GIS/uscomp/n0r_${ftime}.wld wld" n0r${ftime}.tfw


rm -f n0r${ftime}.tfw test_$$.png net_$$_in.tif n0r_$$_in.tif n0r_$$_out.tif
