import pandas as pd
from pathlib import Path

p = Path(r'data/processed/training')

frames = []
for pp in p.glob("*.csv"):
    print('Reading', str(pp))
    df = pd.read_csv(str(pp))
    frames.append(df)

df = pd.concat(frames)
#df.to_csv('data/processed/training_v3.csv')
df.to_pickle('data/processed/training_v3.pkl')
