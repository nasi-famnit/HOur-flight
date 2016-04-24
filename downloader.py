import os
import re

from datetime import date, timedelta
from urllib import request
from pathlib import Path
from urlpath import URL
from zipfile import ZipFile

import flightdata
import airportcodes

def iter_days(start_date:date, end_date:date):
    cur = start_date
    delta = timedelta(days=1)
    while cur < end_date:
        yield cur
        cur += delta

def iter_months(start_date:date, end_date:date):
    cur = start_date
    prev_month = None
    delta = timedelta(days=1)
    while cur < end_date:
        if cur.month != prev_month:
            yield cur
            prev_month = cur.month
        cur += delta

def download(url, destination_directory):
    dpath = Path(destination_directory)
    url = URL(url)
    fname = url.name
    fpath = dpath / fname

    dpath.mkdir(parents=True, exist_ok = True)

    if fpath.exists():
        print(fname, "already downloaded")
        return fpath
    
    print("Downloading", url.name, 'to', dpath)
    try:
        request.urlretrieve(str(url), str(fpath.absolute()))
        print("...done.")
        return fpath
    except: 
        print('Error occured while downloading', url.name)
        return None

def normalized_strftime_string(s:str):
    if os.name == 'nt':
        return re.sub(r'%-([dmHIMSjUW])', r'%#\1', s)

def download_range(url, destination_directory, start_date, end_date):
    url = normalized_strftime_string(url)
    files_range = None
    if ("%d" in url) or ("%-d" in url):
        files_range = iter_days(start_date, end_date)
    else:
        files_range = iter_months(start_date, end_date)

    downloaded = []
    failed = []
    for timepoint in files_range:
        url_to_download = timepoint.strftime(url)
        path = download(url_to_download, destination_directory)
        if path is not None:
            downloaded.append(path)
        else:
            failed.append(URL(url_to_download).name)
    return downloaded, failed

def download_flights(start_date, end_date):
    files, failed = download_range(r'http://tsdata.bts.gov/PREZIP/On_Time_On_Time_Performance_%Y_%-m.zip', 'data/raw/flights', start_date, end_date)
    dest_path = Path('data/unpacked/flights')
    dest_path.mkdir(parents = True, exist_ok = True)

    airports = set()

    for zip_file in files:
        zf = ZipFile(str(zip_file))
        csv_name = zip_file.with_suffix('.csv').name
        csv_file = dest_path / csv_name
        if not csv_file.exists():
            print("Extracting", csv_name)
            zf.extract(csv_name, str(dest_path))
            print("...done") 
        else:
            print(csv_name, "already extracted")
        df = flightdata.read_csv(str(csv_file))
        airports.update(df.Origin.unique())
    return airports

def download_weather_airport(airport, start_date, end_date):
    icao_id = airportcodes.from_faa(airport)
    urls = [
        (r'ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6405-%Y/64050{}%Y%m.dat', 'asos-onemin'),
        (r'ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6406-%Y/64060{}%Y%m.dat', 'asos-onemin'),
        (r'ftp://ftp.ncdc.noaa.gov/pub/data/asos-fivemin/6401-%Y/64010{}%Y%m.dat', 'asos-fivemin'),
        ]
    weather_path = Path('data/raw/weather')
    for url,folder in urls:
        download_range(url.format(icao_id), weather_path / folder, start_date, end_date)


def download_weather(airports, start_date, end_date):
    for airport in airports:
        download_weather_airport(airport, start_date, end_date)

start_date = date(2016, 1, 1)
end_date = date(2016, 2, 1)

airports = download_flights(start_date, end_date)
download_weather(airports, start_date, end_date)
