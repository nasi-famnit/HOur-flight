import pandas as pd
import numpy as np

from pathlib import Path
from datetime import datetime

import itertools
import airportdata as apc

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
        # 'valid': np.datetime64,
        'lon': np.float32,
        'lat': np.float32,
        'tmpf': np.float32,
        'dwpf': np.float32,
        'relh': np.float32,
        'drct': np.float32,
        'sknt': np.float32,
        'p01i': np.float32,
        'mslp': np.float32,
        'vsby': np.float32,
        'gust': np.float32,
        'skyc1': np.str,
        'skyl1': np.float32,
    }
    df = pd.read_csv(path, parse_dates=['valid'], dtype=dtypes, comment='#', na_values='M', skipinitialspace=True, engine='c')
    if df.shape[0] == 0:
        return None
    df.rename(columns=lambda c: c.strip(), inplace=True)
    df.set_index('valid', inplace=True)

    df['station'] = df['station'].astype('category')
    df['skyc1'] = df['skyc1'].astype('category')

    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].astype('float32')
        if df[col].dtype == 'float32':
            df[col].interpolate('time', inplace=True)
        elif df[col].dtype == 'category':
            df[col].ffill(inplace=True)

    parent_folder = pklpath.parent
    if not parent_folder.exists():
        parent_folder.mkdir(parents=True, exist_ok=True)
    df.to_pickle(str(pklpath))
    iem_cache[path] = df
    return df


def get_weather_conditions(icao, time):
    faa = apc.from_icao(icao)
    # print("Searching for weather at", faa, "t=", time)
    iem_path = Path(r'data/raw/weather/iem-hourly/')
    globbed = itertools.chain(iem_path.glob(faa + "*.txt"), iem_path.glob(icao + "*.txt"))
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


if __name__ == '__main__':
    df = read_iem('data/raw/weather/iem/OTH_2015.1-2015.12.csv')
    df.info()
