import pandas as pd
import numpy as np

from pathlib import Path
import pickle

db_pkl_path = "data/processed/airports.pkl"
db_dat_path = "data/raw/airports.dat"
df = None
icao2faa = None
faa2icao = None
by_icao = None
by_iata = None


def init_misc(airports_df):
    global icao2faa, faa2icao, by_icao, by_iata
    pkl_path = 'data/pkl_cache/airports_aux.pkl'
    if Path(pkl_path).exists():
        with open(pkl_path, 'rb') as fin:
            d = pickle.load(fin)
        icao2faa = d['icao2faa']
        faa2icao = d['faa2icao']
        by_icao = d['by_icao']
        by_iata = d['by_iata']
    else:
        icao2faa = {r.ICAO: r.IATA for i, r in airports_df.iterrows()}
        faa2icao = {r.IATA: r.ICAO for i, r in airports_df.iterrows()}
        by_icao = {r.ICAO: r.to_dict() for i, r in airports_df.iterrows()}
        by_iata = {r.IATA: r.to_dict() for i, r in airports_df.iterrows()}
        d = {
            'icao2faa': icao2faa,
            'faa2icao': faa2icao,
            'by_icao': by_icao,
            'by_iata': by_iata
        }
        with open(pkl_path, 'wb') as fout:
            pickle.dump(d, fout)

def init(airports_dat_path):
    columns = ["AirportID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude", "Altitude", "Timezone",
               "DST", "TZTimezone"]
    dtypes = {
        "AirportID": np.uint32,
        "Latitude": np.float64,
        "Longitude": np.float64,
        "Altitude": np.float64,
        "Timezone": np.float32
    }
    df = pd.read_csv(airports_dat_path, header=None, names=columns, dtype=dtypes)
    df.to_pickle('data/processed/airports.pkl')
    init_misc(df)
    return df


if Path(db_pkl_path).exists():
    df = pd.read_pickle(db_pkl_path)
    init_misc(df)
elif Path(db_dat_path).exists():
    df = init(db_dat_path)


def from_faa(faa_id):
    return faa2icao[faa_id]


def from_iata(iata_id):
    return faa2icao[iata_id]


def from_icao(icao_id):
    return icao2faa[icao_id]


def get_faa(faa_id):
    return by_iata[faa_id]


def get_icao(icao_id):
    return by_icao[icao_id]
