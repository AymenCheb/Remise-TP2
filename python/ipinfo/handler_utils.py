"""
Utilities used in handlers.
"""

import json
import os
import sys

from .version import SDK_VERSION

# Base URL to make requests against.
API_URL = "https://ipinfo.io"

# Used to transform incoming responses with country abbreviations into the full
# expanded country name, e.g. "PK" -> "Pakistan".
COUNTRY_FILE_DEFAULT = "countries.json"

COUNTRY_EU_FILE_DEFAULT = "eu.json"

# The max amount of IPs allowed by the API per batch request.
BATCH_MAX_SIZE = 1000

# The default max size of the cache in terms of number of items.
CACHE_MAXSIZE = 4096

# The default TTL of the cache in seconds
CACHE_TTL = 60 * 60 * 24

# The current version of the cached data.
# Update this if the data being cached has changed in shape for the same key.
CACHE_KEY_VSN = "1"

# The default request timeout for per-IP requests.
REQUEST_TIMEOUT_DEFAULT = 2

# The default request timeout for batch requests.
BATCH_REQ_TIMEOUT_DEFAULT = 5


def get_headers(access_token):
    """Build headers for request to IPinfo API."""
    headers = {
        "user-agent": "IPinfoClient/Python{version}/{sdk_version}".format(
            version=sys.version_info[0], sdk_version=SDK_VERSION
        ),
        "accept": "application/json",
    }

    if access_token:
        headers["authorization"] = "Bearer {}".format(access_token)

    return headers


def format_details(details, countries, eu_countries):
    """
    Format details given a countries object.
    """
    details["country_name"] = countries.get(details.get("country"))
    details["isEU"] = details.get("country") in eu_countries
    details["latitude"], details["longitude"] = read_coords(details.get("loc"))


def read_coords(location):
    """
    Given a location of the form `<lat>,<lon>`, returns the latitude and
    longitude as a tuple.

    Returns None for each tuple item if the form is invalid.
    """
    lat, lon = None, None
    coords = tuple(location.split(",")) if location else ""
    if len(coords) == 2 and coords[0] and coords[1]:
        lat, lon = coords[0], coords[1]
    return lat, lon


def read_json_file(json_file):
    """
    Read a list of countries from specified country file or default file.
    """
    json_file = os.path.join(os.path.dirname(__file__), json_file)
    with open(json_file) as f:
        countries_json = f.read()

    return json.loads(countries_json)


def return_or_fail(raise_on_fail, e, v):
    """
    Either throws `e` if `raise_on_fail` or else returns `v`.
    """
    if raise_on_fail:
        raise e
    else:
        return v


def cache_key(k):
    """
    Transforms a user-input key into a versioned cache key.
    """
    return f"{k}:{CACHE_KEY_VSN}"