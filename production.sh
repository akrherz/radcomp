#!/bin/bash
# $1 is the sector
# $2 is the minutes offset

export STARTTIME=$(date -u +'%Y%m%d%H%M%S')

export YYYY=$2
export MM=$3
export DD=$4
export HH=$5
export MI=$6
if [ $7 = "RT" ]; then
    export routes="acr"
else
    export routes="a"
fi
if [ $YYYY -lt 2014 ]; then
    export netprod="NET"
else
    export netprod="EET"
fi

# Our Job ID will be $$
touch ${1}_N0Q_LOCK_$$
touch ${1}_${netprod}_LOCK_$$
sh run_nids.sh $YYYY $MM $DD $HH $MI $$ N0Q $1 &
sh run_nids.sh $YYYY $MM $DD $HH $MI $$ $netprod $1 &

# we need to wait for the above to finish
while [ -e ${1}_N0Q_LOCK_$$  ]; do
  sleep 10
done
while [ -e ${1}_${netprod}_LOCK_$$  ]; do
  sleep 10
done

# Now we are free to produce clean N0Q
python process.py $HH $$ $1 $netprod

# Lets insert it into LDM
pqinsert -p "gis $routes ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/n0q_ GIS/${1,,}comp/n0q_${YYYY}${MM}${DD}${HH}${MI}.png png" ${1}_N0Q_CLEAN_$$.png
# Copy this to data for N0R psuedo to use
if [ $1 = "US" ]; then
    cp ${1}_EET_$$.gif data/eet_${YYYY}${MM}${DD}${HH}${MI}.gif
    cp ${1}_N0Q_CLEAN_$$.png data/n0q_${YYYY}${MM}${DD}${HH}${MI}.png
fi

# Do TFW
python gentfw.py $$ $1 ${YYYY}${MM}${DD}${HH}${MI}
pqinsert -i -p "gis $routes ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/n0q_ GIS/${1,,}comp/n0q_${YYYY}${MM}${DD}${HH}${MI}.wld wld" ${1}_N0Q_CLEAN_$$.tfw

# Send the EET composite to LDM, when in realtime
if [ $7 = "RT" ]; then
    pqinsert -i -p "gis cr ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/eet_ bogus gif" ${1}_${netprod}_$$.gif
    pqinsert -i -p "gis cr ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/eet_ bogus wld" ${1}_N0Q_CLEAN_$$.tfw
fi

# Now, lets create a raw TIF variant, insert compressed to save some bandwidth
magick -compress none ${1}_N0Q_CLEAN_$$.png ${1}_N0Q_CLEAN_$$.tif
magick -compress none ${1}_${netprod}_$$.gif ${1}_${netprod}_$$.tif

# Now, lets create a google TIF variant
gdalwarp  -q -s_srs EPSG:4326 -t_srs EPSG:3857 ${1}_N0Q_CLEAN_$$.tif google_${1}_N0Q_CLEAN_$$.tif
cp ${1}_N0Q_CLEAN_$$.tfw ${1}_${netprod}_$$.tfw
gdalwarp  -q -s_srs EPSG:4326 -t_srs EPSG:3857 ${1}_${netprod}_$$.tif google_${1}_${netprod}_$$.tif
rm ${1}_${netprod}_$$.tfw 

# Compress, insert
gzip -c google_${1}_N0Q_CLEAN_$$.tif > google_${1}_N0Q_CLEAN_$$.tif.Z
gzip -c google_${1}_${netprod}_$$.tif > google_${1}_${netprod}_$$.tif.Z
if [ $7 = "RT" ]; then
    pqinsert -p "gis r ${YYYY}${MM}${DD}${HH}${MI} gis/images/900913/${1}COMP/n0q_ bogus tif.Z" google_${1}_N0Q_CLEAN_$$.tif.Z
    pqinsert -p "gis r ${YYYY}${MM}${DD}${HH}${MI} gis/images/900913/${1}COMP/eet_ bogus tif.Z" google_${1}_${netprod}_$$.tif.Z
fi
# Compress, insert
gzip -c ${1}_N0Q_CLEAN_$$.tif > ${1}_N0Q_CLEAN_$$.tif.Z
gzip -c ${1}_${netprod}_$$.tif > ${1}_${netprod}_$$.tif.Z
if [ $7 = "RT" ]; then
    pqinsert -p "gis r ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/n0q_ bogus tif.Z" ${1}_N0Q_CLEAN_$$.tif.Z
    pqinsert -p "gis r ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/eet_ bogus tif.Z" ${1}_${netprod}_$$.tif.Z
fi

# Cleanup
rm -f google_${1}_${netprod}_$$.tif.Z google_${1}_${netprod}_$$.tif ${1}_${netprod}_$$.tif ${1}_${netprod}_$$.tif.Z
rm -f ${1}_N0Q_CLEAN_$$.png ${1}_N0Q_$$.gif ${1}_${netprod}_$$.gif ${1}_N0Q_CLEAN_$$.tfw 
rm -f ${1}_N0Q_CLEAN_$$.tif.Z ${1}_N0Q_CLEAN_$$.tif google_${1}_N0Q_CLEAN_$$.tif.Z google_${1}_N0Q_CLEAN_$$.tif

# Only do JSON metadata when we are in realtime mode
if [ $7 = "RT" ]; then
    python scripts/create_metadata.py $1 $YYYY $MM $DD $HH $MI N0Q $STARTTIME $$
    python scripts/create_metadata.py $1 $YYYY $MM $DD $HH $MI $netprod $STARTTIME $$
fi

# Remove log files
rm -f logs/*$$.log
