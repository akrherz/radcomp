#set -x

export YYYY="$1"
export YY="`echo $1 | cut -c 3-4`"
export MM="$2"
export DD="$3"
export HH="$4"
export MI="$5"
export JOB="$6"
export PROD="$7"
export SECTOR="$8"


if [ "${SECTOR}" == "US" ]; 
    then
    GRDAREA="23.01;-126.00;50.00;-65.01"
    KXKY="12200;5400"
    STNFIL="conus.tbl"
elif [ "${SECTOR}" == "HI" ];
    then
    GRDAREA="15.44;-162.41;24.44;-152.41"
    KXKY="2000;1800"
    STNFIL="hawaii.tbl"
elif [ "${SECTOR}" == "AK" ];
    then
    GRDAREA="53.21;-170.50;68.71;-130.50"
    KXKY="4000;1550"
    STNFIL="alaska.tbl"
elif [ "${SECTOR}" == "PR" ];
    then
    GRDAREA="13.1;-71.07;23.1;-61.07"
    KXKY="1000;1000"
    STNFIL="PR.tbl"
elif [ "${SECTOR}" == "GU" ];
    then
    GRDAREA="9.20;140.5;17.70;149.0"
    KXKY="1000;1000"
    STNFIL="GU.tbl"
fi

LUTFIL="iem_lut256.tbl"
if [ "$PROD" == "EET" ];
    then
    LUTFIL="iem_eet.tbl"
fi

# Use N0B for N0Q, see akrherz/radcomp#7
REALPROD=$PROD
if [ "$PROD" == "N0Q" ];
    then
    REALPROD="N0B"
fi

#source /usr/local/nawips/Gemenviron.profile
export NA_OS=linux64
export GEMTBL=gempak/tables
export GEMPARM=gempak/param
export GEMPAKHOME=gempak
export CONFIGDIR=gempak/config
export GEMERR=gempak/error
export RAD=/mnt/nexrad3/nexrad/
export GEMPDF=gempak/pdf

./bin/nex2img << EOF > logs/nex2img_${SECTOR}_${PROD}_${JOB}.log
 GRDAREA  = ${GRDAREA}
 PROJ     = CED
 KXKY     = ${KXKY}
 CPYFIL   =  
 GFUNC    = ${REALPROD}
 RADTIM   = ${YY}${MM}${DD}/${HH}${MI}
RADDUR   = 25
 RADFRQ   =
 STNFIL   = ${STNFIL}
 RADMODE  = PC
 RADFIL   = ${SECTOR}_${PROD}_${JOB}.gif
LUTFIL   = ${LUTFIL}
 list
 run

 exit
EOF

rm -f ${SECTOR}_${PROD}_LOCK_${JOB}
