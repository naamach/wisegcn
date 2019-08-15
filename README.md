# WiseGCN

A GCN/TAN (Gamma-ray Coordinates Network/Transient Astronomy Network) handler for use at the Wise Observatory in case of gravitational-wave alerts.

## Getting started

### Prerequisites

* `miniconda` or `anaconda` with `python 3`
* `mysql`
* `git`

### Installing

Create and activate a `conda` environment (named `gw`) with the necessary modules:
```
$ conda create -p /path/to/gw python=3.7.1
$ source activate /path/to/gw
$ pip install pygcn healpy configparser voevent-parse pymysql lxml
$ pip install git+https://github.com/naamach/schedulertml.git
$ pip install git+https://github.com/naamach/wisegcn.git
```
Setup the `mysql` database according to [these instructions](docs/mysql.md).


#### Upgrading
To upgrade `wisegcn` run:
```
$ pip install git+https://github.com/naamach/wisegcn.git --upgrade
```

#### The configuration file

Finally, you will have to provide `wisegcn` with the database credentials and point it to the catalog file and to the directory where you want it to store the event `FITS` files.
To do so, you will need to have a `config.ini` file in the working directory (the directory from which you run the script).
The file should look like that (see `config.ini.example` in the main directory):
```
; config.ini
[GENERAL]
TEST = False ; True - listen ONLY test alerts, change to False to listen to real alerts
BNS_MIN = 0 ; minimal allowed probability of binary neutron star alerts (not including)
NSBH_MIN = 0 ; minimal allowed probability of black hole-neutron star alerts (not including)
BBH_MIN = 999 ; minimal allowed probability of black hole-black hole alerts (not including)
MASSGAP_MIN = 0 ; minimal allowed probability of mass-gap merger alerts (not including)
HASNS_MIN = 0 ; minimal allowed probability the event involved a neutron star (not including)
HASREMNANT_MIN = 0 ; minimal allowed probability the system ejected a non-zero amount of neutron star matter (not including)
TERRESTRIAL_MAX = 999 ; maximal allowed probability of terrestrial alerts (including)
FAR_MAX = 999 ; maximal allowed false alarm rate (including) [1/yr]
AREA_MAX = 999999 ; [deg^2] maximal allowed sky area (including; if the localization is worse, drop the alert)
AREA_CREDZONE = 0.9 ; localization probability to consider credible for AREA_MAX

[LOG]
PATH = /path/to/log/
CONSOLE_LEVEL = DEBUG ; DEBUG, INFO, WARNING, ERROR, CRITICAL
FILE_LEVEL = DEBUG ; DEBUG, INFO, WARNING, ERROR, CRITICAL

[CATALOG]
PATH = /path/to/catalog/
NAME = glade_2.3_RA_Dec

[EMAIL]
FROM = root@example.com
TO = user@example.com
CC = 
BCC = 
SERVER = localhost

[DB]
HOST = localhost
USER = gcn
PASSWD = password
DB = gw
SOCKET = /var/run/mysqld/mysqld.sock

[ALERT FILES]
PATH = /path/to/alerts/

[EVENT FILES]
PATH = /path/to/ligoevent_fits/

[GALAXIES]
CREDZONE = 0.99
RELAXED_CREDZONE = 0.99995
NSIGMAS_IN_D = 3
RELAXED_NSIGMAS_IN_D = 5
COMPLETENESS = 0.5
MINGALAXIES = 100
MAXGALAXIES = 500 ; number of best galaxies to use
MAXGALAXIESPLAN = 100 ; maximal number of galaxies per observation plan
MINMAG = -12 ; magnitude of event in r-band
MAXMAG = -17 ; magnitude of event in r-band
SENSITIVITY = 22
MINDISTFACTOR = 0.01 ; reflecting a small chance that the theory is completely wrong and we can still see something
ALPHA = -1.07 ; Schechter function parameters
MB_STAR = -20.7 ; Schechter function parameters, random slide from https://www.astro.umd.edu/~richard/ASTRO620/LumFunction-pp.pdf but not really...?

[TILE]
CREDZONE = 0.9  ; credible region to cover in tiles
AREA_MAX = 30  ; [deg^2] maximal credible area to tile (including; if larger, observe individual galaxies instead)

[OBSERVING]
SUN_ALT_MAX = -12
BESTEFFORTS = 1
USER = New Observer
EMAIL = user@example.com
DESCRIPTION = 
SOLVE = 1

[WISE]
LAT = 30.59583333333333
LON = 34.763333333333335
ALT = 875
UTC_OFFSET = -2
TELESCOPES = C28  ; C28, C18, 1m
PATH = /path/to/plans/

[C28]
FOV = 1  ; [deg^2] FLI field of view
AIRMASS_MIN = 1.02  ; the shutter blocks the CCD above 80deg
AIRMASS_MAX = 3
HOURANGLE_MIN = -4.6
HOURANGLE_MAX = 4.6
MIN_LUNAR_DIST = 30 ; [deg] minimal lunar distance
FILTER = Luminance
EXPTIME = 300
BINNING = 1
HOST = c28_computer_name ; leave blank to skip plan upload to remote host
USER = username
CYGWIN_PATH = C:\cygwin64\home\username\
PATH = /home/username/

[C18]
FOV = 1  ; [deg^2] SBIG field of view
AIRMASS_MIN = 1
AIRMASS_MAX = 3
HOURANGLE_MIN = -5.3
HOURANGLE_MAX = 5.3
MIN_LUNAR_DIST = 30 ; [deg] minimal lunar distance
FILTER = clearx
EXPTIME = 300
BINNING = 1
HOST = c18_computer_name ; leave blank to skip plan upload to remote host
USER = username
CYGWIN_PATH = C:\cygwin64\home\username\
PATH = /home/username/

[1m]
FOV = 0.2158  ; [deg^2] PI field of view
AIRMASS_MIN = 1
AIRMASS_MAX = 3
HOURANGLE_MIN = -12
HOURANGLE_MAX = 12
MIN_LUNAR_DIST = 30 ; [deg] minimal lunar distance
FILTER = Clear
EXPTIME = 300
BINNING = 1
HOST = 1m_computer_name ; leave blank to skip plan upload to remote host
USER = username
CYGWIN_PATH = C:\cygwin64\home\username\
PATH = /home/username/


[IERS]
URL = ftp://cddis.gsfc.nasa.gov/pub/products/iers/finals2000A.all ; IERS table URL (default is: http://maia.usno.navy.mil/ser7/finals2000A.all)
```

NOTE: To find the `mysql` socket, run:
```
$ netstat -ln | grep mysql
```

The IERS URL option is to solve timeout problems of `wisegcn.observing_tools` functions using `astropy.utils.iers` tables (https://docs.astropy.org/en/stable/utils/iers.html), when the default `http://maia.usno.navy.mil/ser7/finals2000A.all` URL is down.

## Using `wisegcn`

To listen and process public events run (while the `gw` `conda` environment is activated):


```
$ wisegcn-listen
```

This will listen for VOEvents until killed with ctrl+C.

Alternativey, from inside `python` run:

```
import gcn
from wisegcn.handler import process_gcn

print("Listening to GCN notices (press Ctrl+C to kill)...")
gcn.listen(handler=process_gcn)
```

### Testing `wisegcn` offline

To test `wisegcn` offline, first download the sample GCN notice:

```
$ curl -O https://emfollow.docs.ligo.org/userguide/_static/MS181101ab-1-Preliminary.xml
```

Then run:

```
$ wisegcn_localtest
```

Alternativey, from inside `python` run (while the `gw` `conda` environment is activated):

```
from wisegcn.handler import process_gcn
import lxml.etree

print("Assuming MS181101ab-1-Preliminary.xml is in the working directory")
filename = 'MS181101ab-1-Preliminary.xml'

payload = open(filename, 'rb').read()
root = lxml.etree.fromstring(payload)
process_gcn(payload, root)
```

## Additional utilities

You can use `wisegcn` to check the healpix probability of a specific location (based on RA, Dec only, not taking the distance into account), and the localization sky area. These utilities are also Python 2.7 compatible.

### Get healpix probability based on location

```
from wisegcn.utils import get_coo_healpix_probability

ra = 123.45  # [deg]
dec = 12.345  # [deg]
skymap = "/path/to/bayestar.fits.gz"
p = get_coo_healpix_probability(ra, dec, skymap)
```

### Get healpix probability based on GladeID

This part assumes you have configured the `[CATALOG]` part in the `config.ini` file, and the Glade catalog `.npy` file.

```
from wisegcn.utils import get_galaxy_healpix_probability

glade_id = 12345
skymap = "/path/to/bayestar.fits.gz"
p = get_galaxy_healpix_probability(glade_id, skymap)
```

### Get localization sky area based on healpix probability
```
from wisegcn.utils import get_sky_area

credzone = 0.5  # localization probability to consider credible
skymap = "/path/to/bayestar.fits.gz"
area = get_sky_area(skymap, credzone)  # [deg^2]
```

## Acknowledgments
Leo P. Singer, Scott Barthelmy, David Guevel, Michael Zalzman, Sergiy Vasylyev.

`wisegcn` is based on [svasyly/pygcn](https://github.com/svasyly/pygcn), which is based on [lpsinger/pygcn](https://github.com/lpsinger/pygcn).
