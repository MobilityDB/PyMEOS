import pandas as pd
from pymeos import *
ais = pd.read_csv('./data/aisinput.csv')
ais.head()
ais['sog'] = ais.apply(lambda row: TFloatInst(value=row['sog'], timestamp=row['t']), axis=1)
print('Hey')
ais['point'] = ais.apply(lambda row: TGeogPointInst(point=(row['latitude'], row['longitude']), timestamp=row['t']), axis=1)
print('Hey')
ais.drop(['latitude', 'longitude'])
print(ais.head())