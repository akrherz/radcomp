#!/bin/csh
# Special script for gridding the NEXRAD composites

source /mesonet/nawips/Gemenviron
setenv RAD /home/ldm/data/nexrad/
setenv PATH "${PATH}:/home/ldm/bin:/mesonet/local/bin"

set yy="`echo $1 | cut -c 3-4`"
set gtime="$yy$2$3/$4$5"
set ftime="$1$2$3$4$5"

set lut="iem_n0r.tbl"
set radmode="PC"
set routes="acr"
set realtime="t"
if ($# == 7) then
  set realtime="f"
  set routes="a"
endif
set fp="n0r_$$.gif"

# Run nex2img to generate the nationwide composite of N0R!
nex2img << EOF > logs/nex2gini_n0r.log
 GRDAREA  = 24.02;-126.00;50.00;-66.02
 PROJ     = CED
 KXKY     = 6000;2600
 CPYFIL   =  
 GFUNC    = N0R
 RADTIM   = ${gtime}
 RADDUR   = 15
 RADFRQ   =
 STNFIL   = conus.tbl
 RADMODE  = ${radmode}
 RADFIL   = ${fp}
 LUTFIL   = ${lut}
 list
 run

 exit
EOF

if ($realtime == "t") then
  # Some users want the full imagery before I corrupt it below :)
  convert -depth 8 $fp test_$$.png
  pqinsert -p "gis cr ${ftime} gis/images/4326/USCOMP/n0r_full_ bogus png" test_$$.png
  rm -f test_$$.png
endif

# Convert it to TIF for algorithm work
convert -compress none $fp n0r_$$_in.tif
rm -f $fp

# Now generate NET
set fp="net_$$.gif"
nex2img << EOF > logs/nex2gini_net.log
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

if ($realtime == "t") then
  # Insert NET file
  convert -depth 8 $fp test_$$.png
  pqinsert -p "gis cr ${ftime} gis/images/4326/USCOMP/net_ bogus png" test_$$.png
  rm -f test_$$.png
endif

# Convert it to TIF for algorithm work
convert -compress none $fp net_$$_in.tif
rm -f $fp

# Clean it! 
/usr/bin/python gdal-clean.py $$ $1$2$3$4$5

# Convert result file to PNG and send it on its way!
convert -depth 8 n0r_$$_out.tif test_$$.png
pqinsert -p "gis ${routes} ${ftime} gis/images/4326/USCOMP/n0r_ GIS/uscomp/n0r_${ftime}.png png" test_$$.png

# Also insert the world file, so that the archive gets it!
python n0r_gentfw.py ${ftime} n0r
pqinsert -p "gis a ${ftime} bogus GIS/uscomp/n0r_${ftime}.wld wld" n0r${ftime}.tfw

if ($realtime == "t") then
  # Generate GeoTIFF
  geotifcp -e n0r.tfw n0r_$$_out.tif n0r_$$_out.gtif

  # Generate google maps variant
  cp n0r.tfw n0r_$$_out.tfw
  gdalwarp  -q -s_srs EPSG:4326 -t_srs '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_def' n0r_$$_out.tif google_n0r_$$_out.tif
  rm -f n0r_$$_out.tfw

  gzip -c n0r_$$_out.tif > n0r_$$_out.tif.Z
  pqinsert -p "gis r ${ftime} gis/images/4326/USCOMP/n0r_ bogus tif.Z" n0r_$$_out.tif.Z

  gzip -c google_n0r_$$_out.tif > google_n0r_$$_out.tif.Z
  pqinsert -p "gis r ${ftime} gis/images/900913/USCOMP/n0r_ bogus tif.Z" google_n0r_$$_out.tif.Z

  gzip -c n0r_$$_out.gtif > n0r_$$_out.gtif.Z
  pqinsert -p "gis r ${ftime} gis/images/4326/USCOMP/n0r_ bogus gtif.Z" n0r_$$_out.gtif.Z

  # Save a file locally for rotation
  cd tmp/
  foreach i (10 9 8 7 6 5 4 3 2 1 0)
    set j = `echo "${i} + 1" | bc `
    mv n0r_${i}.gif n0r_${j}.gif
  end
  convert ../test_$$.png n0r_0.gif
  gifsicle -U --transparent "#000" --loopcount=0 --delay=100 n0r_11.gif n0r_10.gif  n0r_9.gif n0r_8.gif n0r_7.gif n0r_6.gif n0r_5.gif n0r_4.gif n0r_3.gif n0r_2.gif n0r_1.gif n0r_0.gif  -o anim.gif >& /dev/null
  pqinsert -p "gis c ${ftime} gis/images/4326/USCOMP/n0r_anim_large.gif bogus gif" anim.gif
  gifsicle -U --resize 600x260 --transparent "#000" --loopcount=0 --delay=100 n0r_11.gif n0r_10.gif  n0r_9.gif n0r_8.gif n0r_7.gif n0r_6.gif n0r_5.gif n0r_4.gif n0r_3.gif n0r_2.gif n0r_1.gif n0r_0.gif  -o small.gif >& /dev/null
  pqinsert -p "gis c ${ftime} gis/images/4326/USCOMP/n0r_anim_600x260.gif bogus gif" small.gif
  gifsicle -U --resize 1200x520 --transparent "#000" --loopcount=0 --delay=100 n0r_11.gif n0r_10.gif  n0r_9.gif n0r_8.gif n0r_7.gif n0r_6.gif n0r_5.gif n0r_4.gif n0r_3.gif n0r_2.gif n0r_1.gif n0r_0.gif  -o small.gif >& /dev/null
  pqinsert -p "gis c ${ftime} gis/images/4326/USCOMP/n0r_anim_1200x520.gif bogus gif" small.gif
  
  cd ../
endif

rm -f n0r${ftime}.tfw test_$$.png net_$$_in.tif n0r_$$_in.tif n0r_$$_out.tif n0r_$$_out.tif.Z n0r_$$_out.gtif.Z google_n0r_$$_out.tif.Z google_n0r_$$_out.tif n0r_$$_out.gtif
