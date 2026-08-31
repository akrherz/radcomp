#!/bin/bash

yyyy=$(date --date '1 minute' -u +'%Y')
mm=$(date --date '1 minute' -u +'%m')
dd=$(date --date '1 minute' -u +'%d')
HH=$(date --date '1 minute' -u +'%H')
MM=$(date --date '1 minute' -u +'%M')

if [ -e /tmp/.nexcomp.lock ]; then
  echo "Lock file exists! Evasive Manuver Rikker Gamma"
  kill -9 "$(cat /tmp/.nexcomp.lock)"
  killall nex2img
  rm -f /tmp/.nexcomp.lock
fi

echo $$ > /tmp/.nexcomp.lock

# N0R created via N0Q via N0B
bash n0r.sh "${yyyy}" "${mm}" "${dd}" "${HH}" "${MM}"
# DAA one hour
bash grid.sh "${yyyy}" "${mm}" "${dd}" "${HH}" "${MM}" daa
# DTA storm total
bash grid.sh "${yyyy}" "${mm}" "${dd}" "${HH}" "${MM}" dta

rm -f /tmp/.nexcomp.lock
