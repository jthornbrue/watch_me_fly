from math import cos, radians, sqrt
import unittest

EARTH_METERS_PER_DEGREE_LON = 40075017 / 360
EARTH_METERS_PER_DEGREE_LAT = 40007863 / 360


def distance(runway_lat, runway_lon, runway_n, runway_e, lat, lon):
	"""
	Calculate distance from the runway.

	:param runway_lat: latitude of runway start (degrees)
	:param runway_lon: longitude of runway start (degrees)
	:param runway_n: northing of runway end (relative distance in meters)
	:param runway_e: easting of runway end (relative distance in meters)
	:param lat: latitude of point of interest (degrees)
	:param lon: longitude of point of interest (degrees)
	:return: distance (meters)
	"""

	# We need meters per degree lon at our current latitude.
	earth_meters_per_degree_lon = EARTH_METERS_PER_DEGREE_LON * cos(radians(runway_lat))

	# Length of the runway.
	runway_length = sqrt(runway_n ** 2 + runway_e ** 2)

	assert runway_length > 0, 'Runway must have positive length.'

	# Northing of the point of interest relative to the runway start.
	n = (lat - runway_lat) * EARTH_METERS_PER_DEGREE_LAT

	# Easting of the point of interest relative to the runway start.
	e = (lon - runway_lon) * earth_meters_per_degree_lon

	# Draw a line that includes the runway and extends in both directions.
	# Now find the closest point of approach along this line to our point of interest.
	# The dot product of the point of interest vector with the runway unit vector gives us the distance from the runway start to this closest point.
	d = (n * runway_n + e * runway_e) / runway_length

	if d > runway_length:
		# The closest point is after the runway end, so get the northing and easting relative to the runway end.
		n -= runway_n
		e -= runway_e

	elif d > 0:
		# Find the northing and easting relative to the closest point that is somewhere along the runway.
		n -= d * runway_n / runway_length
		e -= d * runway_e / runway_length

	# Otherwise, the closest point is before the start of the runway, and we already have the northing and easting relative to the runway start.

	# Return the distance to the closest point.
	return sqrt(n ** 2 + e ** 2)


class Test(unittest.TestCase):

	def test_before(self):
		# A point before the start of the SAN runway (Slater's 50/50).
		self.assertAlmostEqual(distance(32.73712, -117.20436, -791, 2751, 32.73824654300916, -117.2123593442412), 759, 0)

	def test_mid(self):
		# The center of the round terminal closest to the center of the runway.
		self.assertAlmostEqual(distance(32.73712, -117.20436, -791, 2751, 32.73276187728815, -117.19621426797755), 255, 0)

	def test_after(self):
		# A point past the end of the SAN runway (PCH and Grape).
		self.assertAlmostEqual(distance(32.73712, -117.20436, -791, 2751, 32.72460070901978, -117.17159350281554), 679, 0)


if __name__ == '__main__':
	unittest.main()
