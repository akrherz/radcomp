#!/bin/csh
# Script to create simple raster by gridding!
# Daryl Herzmann 4 Jul 2003
# 17 Jul 2003: Now we have nex2img!  Thanks Steve
# 25 Jul 2003: Now we are running this on kcci.mesonet, which rocks....
# 31 Mar 2004	Whoaaa, updates.  This is running on newmesonet!
# 21 Apr 2005	Add something to add metadata

source /mesonet/nawips/Gemenviron

#setenv RAD /mesonet/data/nexrad/
setenv RAD /home/ldm/data/nexrad/
setenv PROD ${6}

set yy="`echo $1 | cut -c 3-4`"
#set gtime=`date -u +'%y%m%d/%H%M'`
#set ftime=`date -u +'%Y%m%d%H%M'`
set gtime="$yy$2$3/$4$5"
set ftime="$1$2$3$4$5"
#echo $gtime > aba
#echo $ftime >> aba
#echo $gtime2 >> aba
#echo $ftime2 >> aba
#set dir="/mnt/a1/ARCHIVE/data/${1}/${2}/${3}/GIS/uscomp/"
#mkdir -p ${dir}


#set lut="upc_rad24.tbl"
set lut="iem_n0r.tbl"
set radmode="PC"
set routes="acr"
if (${PROD} == "n1p" || ${PROD} == "ntp" || ${PROD} == "net") then
  set routes="cr"
  set lut = "upc_${PROD}.tbl"
  set radmode=""
endif
set fp="radar_$$.gif"

nex2img << EOF > logs/nex2gini_${PROD}.log
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

  convert -depth 8 $fp test_$$.png
  pqinsert -p "gis ${routes} ${ftime} gis/images/4326/USCOMP/${PROD}_ GIS/uscomp/${PROD}_${ftime}.png png" test_$$.png
  if ($# == 6) then
    convert -compress none test_$$.png test.tif
    #pqinsert -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus tif" test.tif
    geotifcp -e n0r.tfw test.tif test.gtif
    #cp test.tif /mesonet/data/gis/images/unproj/USCOMP/${PROD}_0.tif
    compress test.tif
    compress test.gtif
    pqinsert -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus tif.Z" test.tif.Z
    pqinsert -p "gis r ${ftime} gis/images/4326/USCOMP/${PROD}_ bogus gtif.Z" test.gtif.Z
#    cp test.tif.Z /mesonet/data/gis/images/unproj/USCOMP/${PROD}_0.tif.Z
#    cp test.gtif.Z /mesonet/data/gis/images/unproj/USCOMP/${PROD}_0.gtif.Z
#    cp test_$$.png /mesonet/data/gis/images/unproj/USCOMP/${PROD}_0.png.tmp
#    mv /mesonet/data/gis/images/unproj/USCOMP/${PROD}_0.png.tmp /mesonet/data/gis/images/unproj/USCOMP/${PROD}_0.png
    set dbfts=`date -u +'%d %b %Y %H:%M GMT'`
    #dbfcreate /mesonet/data/gis/images/4326/USCOMP/meta/USCOMP_${PROD}_0.dbf -s ts 100
    #dbfadd /mesonet/data/gis/images/4326/USCOMP/meta/USCOMP_${PROD}_0.dbf "IEM ${PROD} ${dbfts}"
    rm test.*tif* >& /dev/null
  endif

  #if (${PROD} == "n0r") then
  #  cp test_$$.png ${dir}/n0r_${1}${2}${3}${4}${5}.png
  #endif


endif

#./gentfw.py ${ftime} ${PROD}
#pqinsert -p "gis a ${ftime} bogus GIS/uscomp/${PROD}_${ftime}.wld wld" n0r.tfw >& /dev/null
#if (! -e ${dir}/n0r.tfw) then
#  cp n0r.tfw ${dir}/
#endif

rm test_$$.png radar_$$.gif test_$$.gif >& /dev/null
