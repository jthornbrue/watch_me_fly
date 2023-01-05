import pandas as pd
import numpy as np
import json
import pathlib

EARTH_METERS_PER_DEGREE_LON = 40075017 / 360
EARTH_METERS_PER_DEGREE_LAT = 40007863 / 360

airports = pd.read_csv('data/airports.tsv', sep='\t')
print(f'{len(airports)} airports')

runways = json.loads(pathlib.Path('data/Runway_Lines.geojson').read_text())['features']

runways = pd.DataFrame({
	'id': [_['properties']['Loc_Id'] for _ in runways],
	'lat': [min(_['geometry']['coordinates'][0][1], _['geometry']['coordinates'][1][1]) for _ in runways],
	'lon': [min(_['geometry']['coordinates'][0][0], _['geometry']['coordinates'][1][0]) for _ in runways],
	'n': [max(_['geometry']['coordinates'][0][1], _['geometry']['coordinates'][1][1]) for _ in runways],
	'e': [max(_['geometry']['coordinates'][0][0], _['geometry']['coordinates'][1][0]) for _ in runways],
})

print(f'before filtering: {len(runways)} runways from {len(runways.id.unique())} airports')

runways = runways[[_ in set(airports['FAA']) for _ in runways['id']]]

print(f'after filtering: {len(runways)} runways from {len(runways.id.unique())} airports')

# Convert to northing (meters)
runways['n'] = (runways['n'] - runways['lat']) * EARTH_METERS_PER_DEGREE_LAT

# Convert to easting (meters)
runways['e'] = (runways['e'] - runways['lon']) * EARTH_METERS_PER_DEGREE_LON * np.cos(np.radians(runways['lat']))

# Round data to desired precision.
# Five decimal places for lat and lon get us to around 1m accuracy.
runways['lat'] = np.round(runways['lat'], 5)
runways['lon'] = np.round(runways['lon'], 5)

runways['n'] = np.round(runways['n'], 0).astype(int)
runways['e'] = np.round(runways['e'], 0).astype(int)

runways = runways.sort_values(by='id')

# Write as gzipped tab separated value.
# runways.to_csv('data/runways.tsv.gz', index=False, header=True, sep='\t', compression='gzip')

# Write as gzipped tab separated value.
runways.to_csv('data/runways.csv.gz', index=False, header=True, compression='gzip')

# Write as parquet.
# runways.to_parquet('data/runways.parquet', index=False, compression='snappy')
