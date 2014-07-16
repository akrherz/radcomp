#!/bin/bash
# $1 is the sector
# $2 is the minutes offset

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

# Our Job ID will be $$
touch ${1}_N0Q_LOCK_$$
touch ${1}_EET_LOCK_$$
sh run_nids.sh $YYYY $MM $DD $HH $MI $$ N0Q $1 &
sh run_nids.sh $YYYY $MM $DD $HH $MI $$ EET $1 &

# we need to wait for the above to finish
while [ -e ${1}_N0Q_LOCK_$$  ]; do
  sleep 10
done
while [ -e ${1}_EET_LOCK_$$  ]; do
  sleep 10
done

# Now we are free to produce clean N0Q
python process.py $HH $$ $1

# Lets insert it into LDM
/home/ldm/bin/pqinsert -p "gis $routes ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/n0q_ GIS/${1,,}comp/n0q_${YYYY}${MM}${DD}${HH}${MI}.png png" ${1}_N0Q_CLEAN_$$.png

# Do TFW
python gentfw.py $$ $1 ${YYYY}${MM}${DD}${HH}${MI}
/home/ldm/bin/pqinsert -p "gis a ${YYYY}${MM}${DD}${HH}${MI} bogus GIS/${1,,}comp/n0q_${YYYY}${MM}${DD}${HH}${MI}.wld wld" ${1}_N0Q_CLEAN_$$.tfw


# Now, lets create a raw TIF variant, insert compressed to save some bandwidth
convert -compress none ${1}_N0Q_CLEAN_$$.png ${1}_N0Q_CLEAN_$$.tif

# Now, lets create a google TIF variant
gdalwarp  -q -s_srs EPSG:4326 -t_srs '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_def' ${1}_N0Q_CLEAN_$$.tif google_${1}_N0Q_CLEAN_$$.tif

# Compress, insert
gzip -c google_${1}_N0Q_CLEAN_$$.tif > google_${1}_N0Q_CLEAN_$$.tif.Z
if [ $7 = "RT" ]; then
	/home/ldm/bin/pqinsert -p "gis r ${YYYY}${MM}${DD}${HH}${MI} gis/images/900913/${1}COMP/n0q_ bogus tif.Z" google_${1}_N0Q_CLEAN_$$.tif.Z
fi
# Compress, insert
gzip -c ${1}_N0Q_CLEAN_$$.tif > ${1}_N0Q_CLEAN_$$.tif.Z
if [ $7 = "RT" ]; then
	/home/ldm/bin/pqinsert -p "gis r ${YYYY}${MM}${DD}${HH}${MI} gis/images/4326/${1}COMP/n0q_ bogus tif.Z" ${1}_N0Q_CLEAN_$$.tif.Z
fi

# Cleanup
rm -f ${1}_N0Q_CLEAN_$$.png ${1}_N0Q_$$.gif ${1}_NET_$$.gif ${1}_N0Q_CLEAN_$$.tfw 
rm -f ${1}_N0Q_CLEAN_$$.tif.Z ${1}_N0Q_CLEAN_$$.tif google_${1}_N0Q_CLEAN_$$.tif.Z google_${1}_N0Q_CLEAN_$$.tif

python scripts/create_metadata.py $1 $YYYY $MM $DD $HH $MI N0Q
python scripts/create_metadata.py $1 $YYYY $MM $DD $HH $MI NET
