import pandas as pd

#names = ['ID', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Latitude', 'Longitude', 'Altitude', 'Timezone', 'DST', 'TzTimezone']
df = pd.read_pickle('data/processed/airports.pkl')
#df['FAA'] = df['IATA']

icao2faa = {r.ICAO : r.IATA for i, r in df.iterrows()}
faa2icao = {r.IATA : r.ICAO for i, r in df.iterrows()}

def from_faa(id):
    return faa2icao[id]

def from_iata(id):
    return faa2icao[id]

def from_icao(id):
    return icao2faa[id]