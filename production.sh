#!/bin/bash

export YYYY="`date --date '1 minute' -u +%Y`"
export MM="`date --date '1 minute' -u +%m`"
export DD="`date --date '1 minute' -u +%d`"
export HH="`date --date '1 minute' -u +%H`"
export MI="`date --date '1 minute' -u +%M`"

# Our Job ID will be $$
touch N0Q_LOCK_$$
touch NET_LOCK_$$
sh run_nids.sh $YYYY $MM $DD $HH $MI $$ N0Q &
sh run_nids.sh $YYYY $MM $DD $HH $MI $$ NET &

# we need to wait for the above to finish
while [ -e N0Q_LOCK_$$  ]; do
  sleep 10
done
while [ -e NET_LOCK_$$  ]; do
  sleep 10
done

# Now we are free to produce clean N0Q
python process.py $HH $$

# Lets insert it into LDM
/home/ldm/bin/pqinsert -p 'gis acr ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/USCOMP/n0q_ GIS/uscomp/n0q_${YYYY}${MM}${DD}${HH}${MI}.png png' N0Q_CLEAN_$$.png

# Do TFW
python gentfw.py
/home/ldm/bin/pqinsert -p 'gis a ${YYYY}${MM}${DD}${HH}${MI} bogus GIS/uscomp/n0q_${YYYY}${MM}${DD}${HH}${MI}.wld wld' $$.tfw

# Cleanup
rm -f N0Q_CLEAN_$$.png N0Q_$$.gif NET_$$.gif $$.tfw