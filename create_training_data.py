import flightdata
import weatherparser
import airportdata

import pandas as pd
from datetime import datetime
from pathlib import Path

flights = flightdata.read_csv('data/unpacked/flights/On_Time_On_Time_Performance_2016_1.csv')
fname = 'data/processed/training/training{:04}_v1.csv'

prev_time = datetime.now()

df = pd.DataFrame()

current_csv_name = Path(fname.format(1))

for idx, flight in flights.iterrows():
    idx = idx+1
    if idx%100 == 0:
        now_time = datetime.now()
        delta = now_time - prev_time
        print('Processing file', idx, ',', 100.0/delta.total_seconds(), 'per second')
        prev_time = now_time
        if idx % 1000 == 0:
            ff = fname.format(idx//1000)
            current_csv_name = Path(fname.format(1+idx//1000))
            print('Writing to', ff)
            df.to_csv(ff)
    else:
        if current_csv_name.exists():
            continue
    ff = flight[['Year', 'Month', 'DayofMonth', 'DayOfWeek', 'UniqueCarrier', 'Origin', 'Dest', 'CRSDepTime', 'DepDelayMinutes', 'DepDel15', 'CRSArrTime', 'ArrTime', 'ArrDelay', 'ArrDelayMinutes', 'ArrDel15', 'CRSElapsedTime', 'ActualElapsedTime', 'Distance', 'WeatherDelay']]
    weather_origin = weatherparser.get_weather_conditions(airportdata.from_faa(ff.Origin), ff.CRSDepTime)
    weather_dest = weatherparser.get_weather_conditions(airportdata.from_faa(ff.Dest), ff.CRSArrTime)
    if (weather_origin is None) or ( weather_dest is None):
        continue
    line = pd.DataFrame(pd.concat([ff, weather_origin, weather_dest])).T
    if idx%1000==1:
        df = line
    else:
        df = df.append(line)
