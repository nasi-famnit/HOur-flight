import requests
from datetime import datetime, timedelta, tzinfo
import arrow
from arrow.arrow import Arrow
import re
import pandas as pd
from io import StringIO
from lxml import etree

import airportcodes

def special_time_format(t):
    return re.sub(r':([\d][\d])$', r'\1', t)

def request_weather(location, time):
    if isinstance(time, str) :
        start_time = arrow.get(time)
    else:
        start_time = time
    start_time = start_time.replace(microsecond=0)
    end_time = start_time + timedelta(hours=1)
    url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam"
    querystring = {
        "dataSource":"tafs",
        "requestType":"retrieve",
        "format":"xml",
        "stationString":airportcodes.from_faa(location),
        "startTime":special_time_format(start_time.isoformat()),
        "endTime":special_time_format(end_time.isoformat()),
        "mostRecent":'true'
        }

    headers = {
        'cache-control': "no-cache",
        }
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    t = etree.fromstring(response.text.encode('utf-8'))
    taf = t.find('data').find('TAF')
    forecast = taf.find('forecast')
    return {'drct':forecast.find('wind_dir_degrees').text,
            'sknt':forecast.find('wind_speed_kt').text,
            'vsby':forecast.find('visibility_statute_mi').text,
            'skyc1':forecast.find('sky_condition').get('sky_cover'),
            'skyl1':forecast.find('sky_condition').get('cloud_base_ft_agl'),
            'lat':taf.find('latitude').text,
            'lon':taf.find('longitude').text
            }

if __name__ == '__main__':
    r = request_weather('LAX', arrow.utcnow() + timedelta(hours=1))
