""" Create the auxillary JSON metadata that goes with this production

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
import sys
import os
import datetime
import tempfile
import subprocess


def main():
    """Go Main Go."""
    sector = sys.argv[1]
    ts = datetime.datetime(
        int(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
        int(sys.argv[5]),
        int(sys.argv[6]),
    )
    utcnow = datetime.datetime.utcnow()
    seconds = (utcnow - ts).days * 86400.0 + (utcnow - ts).seconds
    if seconds > 300:
        sys.exit()
    prod = sys.argv[7]
    job = sys.argv[9]

    starttime = datetime.datetime.strptime(sys.argv[8], "%Y%m%d%H%M%S")
    utcnow = datetime.datetime.utcnow()

    radars = 0
    used = 0
    logfn = "logs/nex2img_%s_%s_%s.log" % (sector, prod, job)
    if os.path.isfile(logfn):
        for line in open(logfn):
            if line.find("Searching radar:") > 0:
                radars += 1
            elif line.find("Using image:") > 0:
                used += 1
    else:
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
