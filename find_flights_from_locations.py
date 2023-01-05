import pathlib
import pandas as pd
from distance_from_runway import distance

from log import log

EARTH_METERS_PER_DEGREE_LON = 40075017 / 360
EARTH_METERS_PER_DEGREE_LAT = 40007863 / 360

PREFIX = '0'
DISTANCE_THRESHOLD_METERS = 100
SPEED_THRESHOLD_MPS = 44.704  # 100 mph

filename = pathlib.Path(f'data/loc_{PREFIX}.parquet')
if filename.exists():
	loc = pd.read_parquet(filename)

else:
	loc = pd.read_csv('data/locations.csv').drop(columns='activity').rename(columns={'client_utc_sec': 'ts'})
	loc['ts'] = pd.to_datetime(loc['ts'], unit='s')
	loc = loc[loc['user_id'].str.startswith(PREFIX)]
	loc.to_parquet(filename)

log.info(f'{filename} has {len(loc)} locations from {len(loc.user_id.unique())} users')

runways = pd.read_csv('runways.tsv', sep='\t').rename(columns={'lat': 'runway_lat', 'lon': 'runway_lon', 'n': 'runway_n', 'e': 'runway_e', 'id': 'airport_id'})

# high-speed events
hs = loc[loc.speed > SPEED_THRESHOLD_MPS]
hs = hs.merge(runways, how='cross')

hs['distance'] = [distance(runway_lat, runway_lon, runway_n, runway_e, lat, lon) for runway_lat, runway_lon, runway_n, runway_e, lat, lon in zip(hs['runway_lat'], hs['runway_lon'], hs['runway_n'], hs['runway_e'], hs['latitude'], hs['longitude'])]

hs = hs[hs['distance'] < DISTANCE_THRESHOLD_METERS]

hs = hs.loc[hs.groupby('user_id')['distance'].idxmin()][['user_id', 'distance', 'airport_id']]

loc = loc.merge(hs, on='user_id')

loc.groupby('user_id').apply(lambda _: _.to_csv(f'takeoffs/takeoff_{_.name}.tsv', header=True, index=False, sep='\t'))

