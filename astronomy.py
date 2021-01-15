from datetime import datetime

from astropy.coordinates import get_body, get_constellation
from astropy.coordinates import solar_system_ephemeris
from astropy.time import Time
from persiantools import digits
from persiantools.jdatetime import JalaliDateTime

from constants import constellation_names_dict, constellation_symbol_dict


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


def get_moon_txt():
    moon_name = "قمر در "

    angle, constellation = get_planet_position('moon')
    sidereal_constellation_txt = moon_name + constellation_names_dict.get(constellation, constellation)
    sidereal_symbol = constellation_symbol_dict.get(constellation, constellation)
    tropical_constellation = int(angle / 30)
    tropical_constellation_angle = int(angle % 30)
    tropical_constellation_txt = moon_name + list(constellation_names_dict.values())[
        tropical_constellation] + " " + str(
        tropical_constellation_angle) + "درجه"
    tropical_symbol = list(constellation_symbol_dict.values())[tropical_constellation]

    txt = "》بسم الله الرحمن الرحیم《\n\n"
    JalaliDateTime.locale = "fa"
    jalali_date = JalaliDateTime.now().strftime("%Y / %m / %d")
    jalali_time = JalaliDateTime.now().strftime("%H:%M")
    txt += "```\n" + jalali_date + "\n" + jalali_time + "\n\n" + "```"
    txt += """
✅ برج فلکی 👈🏻            {tropical_symbol}
{tropical}

✅ صورت فلکی 👈🏻        {sidereal_symbol}
{sidereal}

کانال ما:
@tanjimestan
ربات ما:
@tanjimestan_bot

""".format(tropical_symbol=tropical_symbol, tropical=tropical_constellation_txt,
                       sidereal_symbol=sidereal_symbol, sidereal=sidereal_constellation_txt)

    return digits.en_to_fa(txt)
    #
    # if constellation == 'Scorpius' or 270.0 > angle >= 240.0:
    #     return moon_name + constellation_names_dict.get(constellation, constellation)
    # if constellation == 'Scorpius' or 270.0 > angle >= 240.0:
    #     return "قمر در سور"
