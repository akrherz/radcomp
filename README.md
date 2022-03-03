# NEXRAD Compositing

This is a suite of scripts that proctor the execution of GEMPAK's nex2img to
create NEXRAD composites.  [See IEM Website](https://mesonet.agron.iastate.edu/docs/nexrad_composites/)

**Instead of using this**, you really should just use [MRMS](https://www.nssl.noaa.gov/projects/mrms/) and download data from their [website](http://mrms.ncep.noaa.gov/data/).  I do provide an archive of selected grib files [here](http://mtarchive.geol.iastate.edu/).

## Build status

Limited integration testing is done on Github Actions: [![Build Status](https://github.com/akrherz/radcomp/workflows/Install%20and%20Test/badge.svg)](https://github.com/akrherz/radcomp/actions)

## nex2img code difference

This repo bundles a RHEL8 built `nex2img` with the following diff applied. This
allows some logging to come to stderr, which is then used to produce metadata on
how many RADARs went into the composite.

```diff
diff --git a/gempak/source/programs/upc/programs/nex2img/nex2img.f b/gempak/source/programs/upc/programs/nex2img/nex2img.f
index 02abdc82..3737b9c8 100644
--- a/gempak/source/programs/upc/programs/nex2img/nex2img.f
+++ b/gempak/source/programs/upc/programs/nex2img/nex2img.f
@@ -218,6 +218,7 @@ C
                        CALL TB_RSTN(ilun,stid,stnnam, istnm, stat,
      +                    coun, slat, slon, selv, ispri, tbchars,
      +                    ierf )
+                        write(*,*) 'Searching radar: ', stid
                         IF (ierf.eq.0) THEN
                           viewable = .true.
                           ifile = 1
@@ -256,6 +257,7 @@ C
                              radproj = 'RAD|D'
                              radarea = 'dset'
                              idrpfl = 0
+                              write(*,*) 'Using image: ', imgfls
                               CALL GG_MAPS ( radproj, radarea, imgfls,
      +                                     idrpfl, ier )
 C
```
