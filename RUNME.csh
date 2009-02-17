#!/bin/csh
# 23 Dec 2003	Make this smarter such that it doesn't just completely stop

set yyyy=`date -u +'%Y'`
set mm=`date -u +'%m'`
set dd=`date -u +'%d'`
set HH=`date -u +'%H'`
set MM=`date -u +'%M'`

if (-e /tmp/.nexcomp.lock) then
 echo "Lock file exists! Evasive Manuver Rikker Gamma"
 rm -f /tmp/.nexcomp.lock
 kill -9 `cat /tmp/.nexcomp.lock`
 killall nex2img
endif

echo $$ > /tmp/.nexcomp.lock

./n0r.csh ${yyyy} ${mm} ${dd} ${HH} ${MM} 
./grid.csh ${yyyy} ${mm} ${dd} ${HH} ${MM} n1p
./grid.csh ${yyyy} ${mm} ${dd} ${HH} ${MM} ntp

foreach rad (DMX DVN ARX MPX FSD OAX ABR UDX EAX)
  ./single.csh ${yyyy} ${mm} ${dd} ${HH} ${MM} $rad
end

rm -f /tmp/.nexcomp.lock
