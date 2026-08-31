#!/bin/bash

export RAD=/mnt/nexrad3/nexrad/
export PATH="${PATH}:/home/meteor_ldm/bin"
export PROD=${6}
export NA_OS=linux64
export GEMTBL=gempak/tables
export GEMPARM=gempak/param
export GEMPAKHOME=gempak
export CONFIGDIR=gempak/config
export GEMERR=gempak/error
export GEMPDF=gempak/pdf


yy=$(echo "$1" | cut -c 3-4)
gtime="$yy$2$3/$4$5"
ftime="$1$2$3$4$5"

fp="radar_$$.gif"

./bin/nex2img << EOF > "logs/nex2img_${PROD}.log"
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

if [ -e "$fp" ]; then

  python scripts/gif2png.py -i $fp -o test_$$.png
  pqinsert -i -p "gis cr ${ftime} gis/images/4326/USCOMP/${PROD}_ GIS/uscomp/${PROD}_${ftime}.png png" test_$$.png
  magick -compress none test_$$.png test.tif
  geotifcp -e n0r.tfw test.tif test.gtif >& /dev/null
  gzip -c test.tif > test.tif.Z
  gzip -c test.gtif > test.gtif.Z
  pqinsert -i -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus tif.Z" test.tif.Z
  pqinsert -i -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus gtif.Z" test.gtif.Z
  rm test.*tif* >& /dev/null

fi

rm test_$$.png radar_$$.gif test_$$.gif >& /dev/null
