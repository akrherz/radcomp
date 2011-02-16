#!/bin/bash
# $1 is the sector
# $2 is the minutes offset

export YYYY=$(date --date "$2 minute" -u +%Y)
export MM=$(date --date "$2 minute" -u +%m)
export DD=$(date --date "$2 minute" -u +%d)
export HH=$(date --date "$2 minute" -u +%H)
export MI=$(date --date "$2 minute" -u +%M)

# Our Job ID will be $$
touch ${1}_N0Q_LOCK_$$
touch ${1}_NET_LOCK_$$
sh run_nids.sh $YYYY $MM $DD $HH $MI $$ N0Q $1 &
sh run_nids.sh $YYYY $MM $DD $HH $MI $$ NET $1 &

# we need to wait for the above to finish
while [ -e ${1}_N0Q_LOCK_$$  ]; do
  sleep 10
done
while [ -e ${1}_NET_LOCK_$$  ]; do
  sleep 10
done

# Now we are free to produce clean N0Q
python process.py $HH $$ $1

# Lets insert it into LDM
/home/ldm/bin/pqinsert -p "gis acr ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/n0q_ GIS/${1,,}comp/n0q_${YYYY}${MM}${DD}${HH}${MI}.png png" ${1}_N0Q_CLEAN_$$.png

# Do TFW
python gentfw.py $$ $1
/home/ldm/bin/pqinsert -p "gis a ${YYYY}${MM}${DD}${HH}${MI} bogus GIS/${1,,}comp/n0q_${YYYY}${MM}${DD}${HH}${MI}.wld wld" ${1}_$$.tfw

# Cleanup
rm -f ${1}_N0Q_CLEAN_$$.png ${1}_N0Q_$$.gif ${1}_NET_$$.gif ${1}_$$.tfw