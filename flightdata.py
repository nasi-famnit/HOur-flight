import pandas as pd
import numpy as np

from pathlib import Path

def read_csv(path):

    csvpath = Path(path).resolve()
    pklpath = Path(str(csvpath).replace('unpacked', 'processed')).with_suffix('.pkl')
    if pklpath.exists():
        return pd.read_pickle(str(pklpath))

    dtypes = {'Year': np.uint16,
              'Quarter': np.uint8,
              'Month': np.uint16,
              'DayofMonth': np.uint8, 
              'DayOfWeek': np.uint8, 
              'FlightDate': np.str,
              'UniqueCarrier': np.str,
              "AirlineID": np.uint32,
              "Origin": np.str,
              "OriginState": np.str,
              "OriginStateFips": np.uint8,
              "Dest": np.str,
              "DestState": np.str,
              "DestStateFips": np.str,
              "CRSDepTime": np.str, #scheduled departure time
              "DepDelay": np.float32, #departure delay in minutes, positive or negative
              "DepDelayMinutes": np.float32, #departure delay, clamped above 0
              "DepDel15": np.float32, #departure delay greater than 15 min?
              "CRSArrTime": np.str, #scheduled arrival time
              "ArrTime": np.str, #real arrival time
              "ArrDelay": np.float32, #effective arrival delay
              "ArrDelayMinutes": np.float32, #arrival delay, positive
              "ArrDel15": np.float32, #flight was late by more than 15mins
              "CRSElapsedTime": np.float32, #scheduled elapsed time
              "ActualElapsedTime": np.float32, #actual elapsed time
              "Distance": np.float64,
              "CarrierDelay": np.float32,
              "WeatherDelay": np.float32,
              "NASDelay": np.float32,
              "SecurityDelay": np.float32,
              "LateAircraftDelay": np.float32,
              }
    datetimes = []
    useful_columns = list(dtypes.keys()) + list(datetimes)
    
    df = pd.read_csv(path, dtype = dtypes, usecols=useful_columns, parse_dates=datetimes)

    df.CRSDepTime= pd.to_datetime(df.FlightDate+' '+df.CRSDepTime)
    df.CRSArrTime= pd.to_datetime(df.FlightDate+' '+df.CRSArrTime)
    df.FlightDate= pd.to_datetime(df.FlightDate)
    df.UniqueCarrier = df.UniqueCarrier.astype('category')
    df.Origin = df.Origin.astype('category')
    df.Dest = df.Dest.astype('category')
    df.DepDel15 = df.DepDel15.astype('category')

    parent_folder = pklpath.parent
    if not parent_folder.exists():
        parent_folder.mkdir(parents = True, exist_ok = True)
    df.to_pickle(str(pklpath))

    return df

if __name__=='__main__':
    df = read_csv(r'C:\Dev\Projects\flight-ready\data\processed\flights\On_Time_On_Time_Performance_2016_1.csv')