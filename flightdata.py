from pathlib import Path

import numpy as np
import pandas as pd

import airportdata


def read_csv(path):
    csvpath = Path(path).resolve()
    pklpath = Path(str(csvpath).replace('unpacked', 'pkl_cache')).with_suffix('.pkl')
    if pklpath.exists():
        return pd.read_pickle(str(pklpath))

    dtypes = {'Year': np.uint16,
              'Quarter': np.uint8,
              'Month': np.uint8,
              'DayofMonth': np.uint8,
              'DayOfWeek': np.uint8,
              'FlightDate': np.str,
              'UniqueCarrier': np.str,
              "AirlineID": np.uint32,
              "Origin": np.str,
              # "OriginState": np.str,
              # "OriginStateFips": np.uint8,
              "Dest": np.str,
              # "DestState": np.str,
              # "DestStateFips": np.str,
              "CRSDepTime": np.str,  # scheduled departure time
              "DepDelay": np.float32,  # departure delay in minutes, positive or negative
              "DepDelayMinutes": np.float32,  # departure delay, clamped above 0
              "DepDel15": np.float32,  # departure delay greater than 15 min?
              "CRSArrTime": np.str,  # scheduled arrival time
              # "ArrTime": np.str,  # real arrival time
              "ArrDelay": np.float32,  # effective arrival delay
              "ArrDelayMinutes": np.float32,  # arrival delay, positive
              "ArrDel15": np.float32,  # flight was late by more than 15mins
              "CRSElapsedTime": np.float32,  # scheduled elapsed time
              "ActualElapsedTime": np.float32,  # actual elapsed time
              "Distance": np.float32,
              "CarrierDelay": np.float32,
              "WeatherDelay": np.float32,
              "NASDelay": np.float32,
              "SecurityDelay": np.float32,
              "LateAircraftDelay": np.float32,
              }
    datetimes = []
    useful_columns = list(dtypes.keys()) + list(datetimes)

    df = pd.read_csv(path, dtype=dtypes, usecols=useful_columns, parse_dates=datetimes)
    df = df[df.CRSArrTime != "2400"]

    df.CRSDepTime = pd.to_datetime(df.FlightDate + ' ' + df.CRSDepTime)
    df.CRSArrTime = pd.to_datetime(df.FlightDate + ' ' + df.CRSArrTime)
    df.drop('FlightDate', axis=1, inplace=True)

    df.UniqueCarrier = df.UniqueCarrier.astype('category')
    df.Origin = df.Origin.astype('category')
    df.Dest = df.Dest.astype('category')
    df.DepDel15 = df.DepDel15.astype('category')

    df.fillna(
        {"DepDelay": 0, "DepDelayMinutes": 0, "ArrDelay": 0, "ArrDelayMinutes": 0, "WeatherDelay": 0, "NASDelay": 0,
         "SecurityDelay": 0, "LateAircraftDelay": 0, "CarrierDelay": 0}, inplace=True)
    df.dropna(axis=0, inplace=True)

    origin_airports = df.Origin.unique()
    destination_airports = df.Dest.unique()

    for airport in origin_airports:
        where = df.Origin == airport
        ind = pd.DatetimeIndex(df.CRSDepTime[where]).tz_localize(airportdata.by_iata[airport]['TZTimezone'],
                                                                 ambiguous='NaT', errors='coerce').tz_convert('UTC')
        df.loc[where, 'CRSDepTime'] = ind
    for airport in destination_airports:
        where = df.Dest == airport
        ind = pd.DatetimeIndex(df.CRSArrTime[where]).tz_localize(airportdata.by_iata[airport]['TZTimezone'],
                                                                 ambiguous='NaT', errors='coerce').tz_convert('UTC')
        df.loc[where, 'CRSArrTime'] = ind

    df.dropna(axis=0, inplace=True)  # maybe some NaT's have appeared

    parent_folder = pklpath.parent
    if not parent_folder.exists():
        parent_folder.mkdir(parents=True, exist_ok=True)
    df.to_pickle(str(pklpath))

    return df


if __name__ == '__main__':
    df = read_csv('data/unpacked/flights/On_Time_On_Time_Performance_2016_1.csv')
    df.info()
