""" Create the auxillary JSON metadata that goes with this production

{"meta": {"vcp": 212, "product": "N0Q", "valid": "2014-06-25T20:43:55Z",
"site": "DMX"}}

"""
import json
import sys
import os
import datetime
import tempfile
import subprocess

if __name__ == '__main__':
    # Go Main Go
    sector = sys.argv[1]
    ts = datetime.datetime(int(sys.argv[2]), int(sys.argv[3]),
                           int(sys.argv[4]), int(sys.argv[5]),
                           int(sys.argv[6]))
    utcnow = datetime.datetime.utcnow()
    seconds = (utcnow - ts).days * 86400. + (utcnow - ts).seconds
    if seconds > 300:
        sys.exit()
    prod = sys.argv[7]

    starttime = datetime.datetime.strptime(sys.argv[8], '%Y%m%d%H%M%S')
    utcnow = datetime.datetime.utcnow()

    radars = 0
    used = 0
    logfn = "logs/nex2img_%s_%s.log" % (sector, prod)
    if os.path.isfile(logfn):
        for line in open(logfn):
            if line.find("Searching radar:") > 0:
                radars += 1
            elif line.find("Using image:") > 0:
                used += 1

    res = {'meta': {'vcp': None, 'product': prod, 'site': '%sCOMP' % (sector,),
                    'valid': ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'processing_time_secs': (utcnow - starttime).seconds,
                    'radar_quorum': "%s/%s" % (used, radars)}}

    (tmpfp, tmpfn) = tempfile.mkstemp()
    os.write(tmpfp, json.dumps(res))
    os.close(tmpfp)
    cmd = ("/home/ldm/bin/pqinsert -p 'gis r %s gis/images/4326/%sCOMP/%s_"
           " bogus json' %s") % (ts.strftime("%Y%m%d%H%M"), sector,
                                 prod.lower(), tmpfn)
    subprocess.call(cmd, shell=True)
    os.unlink(tmpfn)
