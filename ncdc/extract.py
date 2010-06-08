
import sys, mx.DateTime, glob, os

ts = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

os.chdir("/mesonet/data/nexrad/incoming/")
# Extract tar file
#cmd = "tar -xf N3_N0R_NET_%s.tar" % (ts.strftime("%Y%m%d"),)
#os.system(cmd)
# unzip other files
#os.chdir("nexrad3-herz/%s" % (ts.year,))
#os.chdir("nexrad3-herz/")

files = glob.glob("*%s*.zip" % (ts.strftime("%Y%m%d"),) )
for file in files:
  #KAKQ20030101.tar.Z-herz.zip
  si, so = os.popen2("unzip -o "+ file)
  lines = so.readlines()
  processed = 0
  for line in lines:
    if line.find("extracting:") == -1 and line.find("inflating:") == -1:
      continue
    l3 = line.split()[1]
    # KAKQ_SDUS51_N0RAKQ_200301010004
    nexrad = l3[15:18]
    typ = l3[12:15]
    yyyymmdd = l3[19:27]
    hhmm = l3[27:]
    nd = "/mesonet/data/nexrad/NIDS/%s/%s" % (nexrad,typ)
    if not os.path.isdir(nd):
      os.makedirs(nd)
    nf = "%s_%s_%s" % (typ,yyyymmdd, hhmm)
    os.rename(l3, nd+"/"+nf)
    processed += 1
  #print file, processed
  os.remove(file)
