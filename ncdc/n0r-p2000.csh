#!/bin/csh

source /mesonet/nawips/Gemenviron

setenv RAD /mesonet/data/nexrad/

set yy="`echo $1 | cut -c 3-4`"
set gtime="$yy$2$3/$4$5"
set ftime="$1$2$3$4$5"

set lut="iem_n0r.tbl"
set radmode="PC"
set routes="acr"
set routes2="cr"
set routes3="r"
if ($# == 7) then
  set routes="a"
  set routes2="o"
  set routes3="o"
endif
set fp="radar_$$.gif"


while (! -e $fp)
  rm -f log
  strace -eopen -o log nex2img << EOF >& logs/nex2gini_n0r.log
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

EOF
  if (! -e ${fp}) then
   set badfile="`grep N0R_ log | tail -1  | cut -c 7-58`"
   set nexrad="`grep N0R_ log | tail -1  | cut -c 34-36`"
   echo "The bad file is $nexrad $badfile"
   mv $badfile ${nexrad}_${badfile:t}
  endif
end

# Convert it to TIF for algorithm work
magick -compress none $fp n0r_$$_in.tif
rm -f $fp

# Now generate NET


# Clean it! 
#./clean.py $$
#./gdal-clean.py $$ $1$2$3$4$5

# Lets finish up, finally
magick -depth 8 n0r_$$_in.tif test_$$.png
pqinsert -q /home/ldm/ldm.pq -p "gis ${routes} ${ftime} gis/images/4326/USCOMP/n0r_ GIS/uscomp/n0r_${ftime}.png png" test_$$.png

./gentfw.py ${ftime} n0r
pqinsert -q /home/ldm/ldm.pq -p "gis a ${ftime} bogus GIS/uscomp/n0r_${ftime}.wld wld" n0r${ftime}.tfw


rm -f n0r${ftime}.tfw test_$$.png net_$$_in.tif n0r_$$_in.tif n0r_$$_out.tif
