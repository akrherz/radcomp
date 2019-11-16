#!/bin/csh
# Script to create simple raster by gridding!
# Daryl Herzmann 4 Jul 2003
# 17 Jul 2003: Now we have nex2img!  Thanks Steve
# 25 Jul 2003: Now we are running this on kcci.mesonet, which rocks....
# 31 Mar 2004	Whoaaa, updates.  This is running on newmesonet!
# 21 Apr 2005	Add something to add metadata

setenv RAD /mnt/nexrad3/nexrad/
setenv PATH "${PATH}:/home/ldm/bin:/mesonet/local/bin"
setenv PROD ${6}
setenv NA_OS linux64
setenv GEMTBL gempak/tables
setenv GEMPARM gempak/param
setenv GEMPAKHOME gempak
setenv CONFIGDIR gempak/config
setenv GEMERR gempak/error
setenv GEMPDF gempak/pdf


set yy="`echo $1 | cut -c 3-4`"
set gtime="$yy$2$3/$4$5"
set ftime="$1$2$3$4$5"

#set lut="upc_rad24.tbl"
set lut = "upc_${PROD}.tbl"
set radmode=""
set fp="radar_$$.gif"

./bin/nex2img << EOF > logs/nex2img_${PROD}.log
 GRDAREA  = 24.02;-126.00;50.00;-66.02
 PROJ     = CED
 KXKY     = 6000;2600
 CPYFIL   =  
 GFUNC    = ${PROD}
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

if (-e $fp) then

  convert -define PNG:preserve-colormap $fp test_$$.png >& /dev/null
  pqinsert -p "gis cr ${ftime} gis/images/4326/USCOMP/${PROD}_ GIS/uscomp/${PROD}_${ftime}.png png" test_$$.png >& /dev/null
  convert -compress none test_$$.png test.tif
  geotifcp -e n0r.tfw test.tif test.gtif
  gzip -c test.tif > test.tif.Z
  gzip -c test.gtif > test.gtif.Z
  pqinsert -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus tif.Z" test.tif.Z >& /dev/null
  pqinsert -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus gtif.Z" test.gtif.Z >& /dev/null
  rm test.*tif* >& /dev/null

endif

rm test_$$.png radar_$$.gif test_$$.gif >& /dev/null
