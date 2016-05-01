import pandas as pd
import numpy as np

from pathlib import Path
from datetime import datetime

import itertools
import airportdata as apc

def read_6405(path):
    names =[
        'ICAO_WBAN', 
        'FAA_timestamp', 
        'VisCoeff1',
        'VisCoeff1ND',
        'VisCoeff2',
        'VisCoeff2ND',
        'WindDirDeg2min', 
        'WindSpeed2min', 
        'WindDirDeg5sec', 
        'WindSpeed5sec',
        'RunwayVisualRange'
        ]
    df = pd.read_fwf(path, header=None, names = names, na_values = ['M'])
    df['VisCoeff1ND'] = df['VisCoeff1ND'].astype('category')
    df['VisCoeff2ND'] = df['VisCoeff2ND'].astype('category')

    #df['WindDirDeg2min'] = df['WindDirDeg2min'].astype(np.float32)

    return df

def read_6406(path):
    names =[
        'ICAO_WBAN', 
        'FAA_timestamp', 
        'PercipID',
        #'Unknown1',
        #'Unknown2',
        'PercipAmt', 
        'FrozenPercipFreq',
        'PressuremmHg',
        'DryBulbTemp', 
        'DewPtTemp'
        ]
    df = pd.read_csv(path, header=None, sep = r'[ \t\[\]]+',  names = names, na_values = ['M'])
    df['PercipID'] = df['PercipID'].astype('category')

    #df['WindDirDeg2min'] = df['WindDirDeg2min'].astype(np.float32)

    return df

iem_cache = dict()

def read_iem(path):
    if path in iem_cache:
        return iem_cache[path]
    csvpath = Path(path).resolve()
    pklpath = Path(str(csvpath).replace('raw', 'pkl_cache')).with_suffix('.pkl')
    if pklpath.exists():
        return pd.read_pickle(str(pklpath))

    dtypes = {
        'station': np.str,
        #'valid': np.datetime64,
        'lon': np.float32,
        'lat': np.float32,
        'tmpf': np.float32,
        'dwpf': np.float32,
        'relh': np.float32,
        'drct': np.float32,
        'skcnt': np.float32,
        'p01i': np.float32,
        'alti': np.float32,
        'mslp': np.float32,
        'vsby': np.float32,
        'gust': np.float32,
        'skyc1': np.str,
        'skyc2': np.str,
        'skyc3': np.str,
        'skyc4': np.str,
        'skyl1': np.float32,
        'skyl2': np.float32,
        'skyl3': np.float32,
        'skyl4': np.float32,
        'presentwx': np.str,
        'metar': np.str
        }
    df = pd.read_csv(path, parse_dates = ['valid'], dtype=dtypes,comment='#', na_values='M', error_bad_lines=False, warn_bad_lines=True, skipinitialspace=True)
    df.set_index(pd.DatetimeIndex(df.valid), inplace=True)
    df.drop('metar', 1, inplace = True)

    parent_folder = pklpath.parent
    if not parent_folder.exists():
        parent_folder.mkdir(parents = True, exist_ok = True)
    df.to_pickle(str(pklpath))
    iem_cache[path] = df
    return df

def get_weather_conditions(icao, time):
    faa = apc.from_icao(icao)
    #print("Searching for weather at", faa, "t=", time)
    iem_path = Path(r'data/raw/weather/iem-hourly/')
    globbed = itertools.chain(iem_path.glob(faa+"*.txt") , iem_path.glob(icao+"*.txt"))
    iem_name = next(globbed, None)
    if iem_name:
        iem_name = str(iem_name)
    else:
        print("Failed weather search at", faa, "t=", time)
        return None
    df = read_iem(iem_name)
    if df.empty:
        return None
    if time < df.valid.min():
        return df.iloc[0]
    else:
        return df.loc[df.valid.asof(time)]

if __name__=='__main__':
    wc = get_weather_conditions('KSLC', datetime(2016, 1, 1, 0, 20))
