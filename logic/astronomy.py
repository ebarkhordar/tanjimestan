from datetime import datetime

from astropy.coordinates import get_body, get_constellation
from astropy.coordinates import solar_system_ephemeris
from astropy.time import Time


def get_planet_position(body='moon', specific_datetime=None):
    if specific_datetime is None:
        specific_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
        # today_date = datetime.now().strftime("2021-01-9 %H:%M")
    t = Time(specific_datetime)
    with solar_system_ephemeris.set('builtin'):
        sky_coord = get_body(body, t)
        constellation = get_constellation(sky_coord)
        ra = sky_coord.ra
        angle = float(ra.to_string(decimal=True))
        return angle, constellation


