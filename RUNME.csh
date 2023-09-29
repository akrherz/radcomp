#!/bin/csh

set yyyy=`date --date '1 minute' -u +'%Y'`
set mm=`date --date '1 minute' -u +'%m'`
set dd=`date --date '1 minute' -u +'%d'`
set HH=`date --date '1 minute' -u +'%H'`
set MM=`date --date '1 minute' -u +'%M'`

if (-e /tmp/.nexcomp.lock) then
 echo "Lock file exists! Evasive Manuver Rikker Gamma"
 rm -f /tmp/.nexcomp.lock
 kill -9 `cat /tmp/.nexcomp.lock`
 killall nex2img
endif

echo $$ > /tmp/.nexcomp.lock

# N0R created via N0Q via N0B
./n0r.csh ${yyyy} ${mm} ${dd} ${HH} ${MM}
# DAA one hour
./grid.csh ${yyyy} ${mm} ${dd} ${HH} ${MM} daa
# DTA storm total
./grid.csh ${yyyy} ${mm} ${dd} ${HH} ${MM} dta
#./grid.csh ${yyyy} ${mm} ${dd} ${HH} ${MM} n1p
#./grid.csh ${yyyy} ${mm} ${dd} ${HH} ${MM} ntp

rm -f /tmp/.nexcomp.lock
