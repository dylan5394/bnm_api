from fuzzywuzzy import fuzz
from math import radians, cos, sin, asin, sqrt


def haversine(user_lon, user_lat, store_lon, store_lat, radius):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    user_lon = float(user_lon)
    user_lat = float(user_lat)
    store_lon = float(store_lon)
    store_lat = float(store_lat)
    # convert decimal degrees to radians
    user_lon, user_lat, store_lon, store_lat = map(radians, [user_lon, user_lat, store_lon, store_lat])

    # haversine formula
    dlon = store_lon - user_lon
    dlat = store_lat - user_lat
    a = sin(dlat/2)**2 + cos(user_lat) * cos(store_lat) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 3956  # Radius of earth in miles. Use 6371 for kilometers.
    return c * r <= float(radius)


def fuzzy_match(string1, string2):
    return fuzz.token_set_ratio(string1, string2) >= 50
