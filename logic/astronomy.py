from datetime import datetime

from astropy.coordinates import get_body, get_constellation
from astropy.coordinates import solar_system_ephemeris
from astropy.time import Time
from persiantools import digits
from persiantools.jdatetime import JalaliDateTime

from constants import constellation_names_dict, tropical_index_names_dict


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


def get_persian_name_of_constellation(constellation_en):
    return constellation_names_dict.get(constellation_en)[0]


def get_persian_symbol_of_constellation(constellation_en):
    return constellation_names_dict.get(constellation_en)[1]


def get_moon_txt():
    moon_name = "قمر در "

    angle, constellation = get_planet_position('moon')
    sidereal_constellation_txt = moon_name + get_persian_name_of_constellation(constellation)
    sidereal_symbol = get_persian_symbol_of_constellation(constellation)
    tropical_constellation_index = int(angle / 30)
    tropical_constellation_angle = int(angle % 30)
    tropical_name = list(tropical_index_names_dict.keys())[tropical_constellation_index]
    tropical_constellation_txt = moon_name + get_persian_name_of_constellation(tropical_name) + \
                                 " " + str(tropical_constellation_angle) + " درجه"
    tropical_symbol = get_persian_symbol_of_constellation(tropical_name)

    txt = "*بسم الله الرحمن الرحیم*\n\n"
    JalaliDateTime.locale = "fa"
    jalali_date = JalaliDateTime.now().strftime("%Y / %m / %d")
    jalali_time = JalaliDateTime.now().strftime("%H:%M")
    txt += "```\n" + jalali_date + "\n" + jalali_time + "\n" + "```"
    txt += """
✅ برج فلکی 👈🏻            {tropical_symbol}
{tropical}

✅ صورت فلکی 👈🏻        {sidereal_symbol}
{sidereal}

[کانال ما](https://t.me/tanjimestan)
[ربات ما](https://t.me/tanjimestan_bot)

""".format(tropical_symbol=tropical_symbol, tropical=tropical_constellation_txt,
           sidereal_symbol=sidereal_symbol, sidereal=sidereal_constellation_txt)

    return digits.en_to_fa(txt)
    #
    # if constellation == 'Scorpius' or 270.0 > angle >= 240.0:
    #     return moon_name + constellation_names_dict.get(constellation, constellation)
    # if constellation == 'Scorpius' or 270.0 > angle >= 240.0:
    #     return "قمر در سور"
