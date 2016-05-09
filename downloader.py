import os
import re
from datetime import date, timedelta
from pathlib import Path
from urllib import request
from zipfile import ZipFile

import pandas as pd
import requests
from urlpath import URL

import airportdata
import flightdata


def iter_days(start_date: date, end_date: date):
    cur = start_date
    delta = timedelta(days=1)
    while cur < end_date:
        yield cur
        cur += delta


def iter_months(start_date: date, end_date: date):
    cur = start_date
    prev_month = None
    delta = timedelta(days=1)
    while cur < end_date:
        if cur.month != prev_month:
            yield cur
            prev_month = cur.month
        cur += delta


def download(url, destination_directory, filename=None):
    dpath = Path(destination_directory)
    url = URL(url)
    if filename is not None:
        fname = filename
    else:
        fname = url.name
    fpath = dpath / fname

    dpath.mkdir(parents=True, exist_ok=True)

    if fpath.exists():
        print(fname, "already downloaded")
        return fpath

    print("Downloading", fname, 'to', dpath)
    try:
        request.urlretrieve(str(url), str(fpath.absolute()))
        print("...done.")
        return fpath
    except Exception as exception:
        print('Error occured while downloading', fname, ":", exception)
        return None


def normalized_strftime_string(s: str):
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


def merge_flights(frames):
    first_frame = frames[0]
    categorical_columns = (col for col in first_frame.columns if pd.core.common.is_categorical_dtype(first_frame[col]))
    for col in categorical_columns:
        categories = set()
        for frame in frames:
            categories.update(frame[col].cat.categories)

        for frame in frames:
            frame[col].cat.set_categories(categories, inplace=True)
    return pd.concat(frames, copy=False, ignore_index=True)


# can be programmatically downloaded from here:
# http://www.transtats.bts.gov/DL_SelectFields.asp?Table_ID=236&DB_Short_Name=On-Time
def download_flights(start_date, end_date):
    pkl_path = 'data/processed/flights/flights{0}.{1}-{2}.{3}.pkl'.format(start_date.year, start_date.month,
                                                                          end_date.year,
                                                                          end_date.month)
    if Path(pkl_path).exists():
        return pd.read_pickle(pkl_path)
    files, failed = download_range(r'http://tsdata.bts.gov/PREZIP/On_Time_On_Time_Performance_%Y_%-m.zip',
                                   'data/raw/flights', start_date, end_date)
    dest_path = Path('data/unpacked/flights')
    dest_path.mkdir(parents=True, exist_ok=True)

    frames = []

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
        frames.append(df)

    all_flights = merge_flights(frames)
    all_flights.to_pickle(pkl_path)
    return all_flights


def download_weather_airport(airport, start_date, end_date):
    url = "http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
    params = {"tz": "Etc/UTC",
              "format": "comma",
              "year1": str(start_date.year), "month1": str(start_date.month), "day1": str(start_date.day),
              "year2": str(end_date.year), "month2": str(end_date.month), "day2": str(end_date.day),
              "station": airport,
              "latlon": "yes",
              "data": ["tmpf", "dwpf", "relh", "drct", "sknt", "p01i", "mslp", "vsby", "gust", "skyc1", "skyl1"]
              }
    filename = '{}_{}.{}-{}.{}.csv'.format(airport, start_date.year, start_date.month,
                                           end_date.year,
                                           end_date.month)
    r = requests.Request(method='GET', url=url, params=params).prepare()
    download(r.url, 'data/raw/weather/iem', filename=filename)


def download_weather(airports, start_date, end_date):
    n_airports = len(airports)
    print("Will download weather data for", n_airports, "airports")
    i = 1
    for airport in airports:
        print(i, ": ", end='')
        i += 1
        download_weather_airport(airport, start_date, end_date)


def download_airport_data():
    url = "https://cdn.rawgit.com/dancsi/5badd4887a43b998ea3b549b3a0e4e81" \
          "/raw/e6e761816c84193fca58218b62aba713b36d9dae/airports.dat"
    fpath = download(url, 'data/raw/')
    airportdata.init(fpath)


start_date = date(2015, 1, 1)
end_date = date(2015, 12, 31)

download_airport_data()

flights = download_flights(start_date, end_date)
airports = set(flights['Origin']) | set(flights['Dest'])

download_weather(airports, start_date, end_date)
