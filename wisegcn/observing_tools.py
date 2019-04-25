from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
from astropy import units as u
from astropy.time import Time
import numpy as np


def is_night(lat, lon, alt, t=Time.now(), sun_alt_twilight=-12*u.deg):
    """is it nighttime?"""

    obs = EarthLocation(lat=lat, lon=lon, height=alt)
    sun_altaz = get_sun(t).transform_to(AltAz(obstime=t, location=obs))
    if sun_altaz.alt > sun_alt_twilight:
        return False

    return True


def next_sunset(lat, lon, alt, t=Time.now(), sun_alt_twilight=-12*u.deg):
    """when is next sunset?"""
    obs = EarthLocation(lat=lat, lon=lon, height=alt)
    t_vec = t + np.arange(0, 24*60, 1) * u.minute
    sun_altaz = get_sun(t_vec).transform_to(AltAz(obstime=t_vec, location=obs))
    night_idx = np.where(sun_altaz.alt < sun_alt_twilight)[0]
    if night_idx[0] != 0:
        # Sun hasn't set yet:
        sunset_idx = night_idx[0]
    else:
        # it's night now, finding next sunset:
        sunset_idx = night_idx[np.where(np.diff(night_idx) > 1)[0] + 1]
    return t_vec[sunset_idx]


def next_sunrise(lat, lon, alt, t=Time.now(), sun_alt_twilight=-12*u.deg):
    """when is next sunrise?"""
    obs = EarthLocation(lat=lat, lon=lon, height=alt)
    t_vec = t + np.arange(0, 24*60, 1) * u.minute
    sun_altaz = get_sun(t_vec).transform_to(AltAz(obstime=t_vec, location=obs))
    night_idx = np.where(sun_altaz.alt > sun_alt_twilight)[0]
    if night_idx[0] != 0:
        # it's night now, finding next sunrise:
        sunrise_idx = night_idx[0] - 1
    else:
        # it's day now, finding next sunrise:
        sunrise_idx = night_idx[np.where(np.diff(night_idx) > 1)[0]]
    return t_vec[sunrise_idx]


def calc_airmass(ra, dec, lat, lon, alt, t=Time.now()):
    obs = EarthLocation(lat=lat, lon=lon, height=alt)
    obj = SkyCoord(ra=ra, dec=dec, frame='icrs')
    obj_altaz = obj.transform_to(AltAz(obstime=t, location=obs))
    airmass = obj_altaz.secz
    return airmass


def calc_hourangle(ra, lon, t=Time.now()):
    lst = t.sidereal_time('apparent', lon)
    ha = lst - ra
    return ha


def is_observable(ra, dec, lat, lon, alt, t=Time.now(), ha_min=-4.6*u.hourangle, ha_max=4.6*u.hourangle,
                  airmass_min=1.02, airmass_max=3, return_values=False):
    # is the object visible?
    airmass = calc_airmass(ra, dec, lat, lon, alt, t)
    if airmass <= airmass_min or airmass >= airmass_max:
        if return_values:
            return False, airmass, 0
        else:
            return False

    # is the hour angle within the limits?
    ha = calc_hourangle(ra, lon, t)
    if ha <= ha_min or ha >= ha_max:
        if return_values:
            return False, airmass, np.double(ha)
        else:
            return False

    if return_values:
        return True, airmass, np.double(ha)
    else:
        return True


def is_observable_in_interval(ra, dec, lat, lon, alt, t1, t2, ha_min=-4.6*u.hourangle, ha_max=4.6*u.hourangle,
                  airmass_min=1.02, airmass_max=3, return_values=False):
    t_vec = t1 + np.arange(0, (t2-t1).to(u.minute), 1) * u.minute

    observable = is_observable(ra, dec, lat, lon, alt, t_vec[0], ha_min, ha_max, airmass_min, airmass_max,
                               return_values=False)
    i = 1
    while (not observable) and (i < len(t_vec)):
        observable, airmass, ha = is_observable(ra, dec, lat, lon, alt, t_vec[i], ha_min, ha_max, airmass_min,
                                                airmass_max, return_values=True)
        i = i + 1

    if return_values:
        return observable, airmass, ha
    else:
        return observable