"""Create the auxillary JSON metadata that goes with this production

{"meta": {"vcp": 212, "product": "N0Q", "valid": "2014-06-25T20:43:55Z",
"site": "DMX"}}

This magic requires that some modifications were done to nex2img to get this
information included in the GEMPAK log file

--- a/gempak/source/programs/upc/programs/nex2img/nex2img.f
+++ b/gempak/source/programs/upc/programs/nex2img/nex2img.f
@@ -221,7 +221,7 @@ C
                         IF (ierf.eq.0) THEN
                           viewable = .true.
                           ifile = 1
-
+                          write(*, *) 'Searching radar: ', stid
                           CALL ST_RPST(tpath,'%SITE%',stid,ipos,
      +                                 outstr, ier)
                           CALL ST_RPST(outstr,'%PROD%',gfunc,ipos,
@@ -256,6 +256,7 @@ C
                              radproj = 'RAD|D'
                              radarea = 'dset'
                              idrpfl = 0
+                             write(*, *) 'Using image: ', imgfls
                               CALL GG_MAPS ( radproj, radarea, imgfls,
      +                                     idrpfl, ier )
 C


"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


def main():
    """Go Main Go."""
    sector = sys.argv[1]
    ts = datetime(
        int(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
        int(sys.argv[5]),
        int(sys.argv[6]),
        tzinfo=timezone.utc,
    )
    utcnow = datetime.now(timezone.utc)
    seconds = (utcnow - ts).days * 86400.0 + (utcnow - ts).seconds
    if seconds > 300:
        sys.exit()
    prod = sys.argv[7]
    job = sys.argv[9]

    starttime = datetime.strptime(sys.argv[8], "%Y%m%d%H%M%S").replace(
        tzinfo=timezone.utc
    )
    utcnow = datetime.now(timezone.utc)

    radars = 0
    used = 0
    logfn = f"logs/nex2img_{sector}_{prod}_{job}.log"
    if os.path.isfile(logfn):
        with open(logfn, encoding="utf-8") as fh:
            for line in fh:
                if line.find("Searching radar:") > 0:
                    radars += 1
                elif line.find("Using image:") > 0:
                    used += 1
    else:
        if prod != "N0R":
            print(f"create_metadata log file {logfn} missing")

    res = {
        "meta": {
            "vcp": None,
            "product": prod,
            "site": "%sCOMP" % (sector,),
            "valid": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "processing_time_secs": (utcnow - starttime).seconds,
            "radar_quorum": "%s/%s" % (used, radars),
        }
    }

    (tmpfp, tmpfn) = tempfile.mkstemp()
    os.write(tmpfp, json.dumps(res).encode("utf-8"))
    os.close(tmpfp)
    cmd = (
        "pqinsert -p 'gis r %s gis/images/4326/%sCOMP/%s_ bogus json' %s"
    ) % (ts.strftime("%Y%m%d%H%M"), sector, prod.lower(), tmpfn)
    subprocess.call(cmd, shell=True)
    os.unlink(tmpfn)


if __name__ == "__main__":
    main()
