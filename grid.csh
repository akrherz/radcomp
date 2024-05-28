#!/bin/csh

setenv RAD /mnt/nexrad3/nexrad/
setenv PATH "${PATH}:/home/meteor_ldm/bin"
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
RADMODE  =
RADFIL   = ${fp}
LUTFIL   = iem_${PROD}.tbl
list
run

exit
EOF

if (-e $fp) then

  python scripts/gif2png.py -i $fp -o test_$$.png
  pqinsert -i -p "gis cr ${ftime} gis/images/4326/USCOMP/${PROD}_ GIS/uscomp/${PROD}_${ftime}.png png" test_$$.png
  magick -compress none test_$$.png test.tif
  geotifcp -e n0r.tfw test.tif test.gtif >& /dev/null
  gzip -c test.tif > test.tif.Z
  gzip -c test.gtif > test.gtif.Z
  pqinsert -i -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus tif.Z" test.tif.Z
  pqinsert -i -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus gtif.Z" test.gtif.Z
  rm test.*tif* >& /dev/null

endif

rm test_$$.png radar_$$.gif test_$$.gif >& /dev/null
