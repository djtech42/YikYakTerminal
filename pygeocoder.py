#!/usr/bin/env python
#
# Xiao Yu - Montreal - 2010
# Based on googlemaps by John Kleint
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Python wrapper for Google Geocoding API V3.

* **Geocoding**: convert a postal address to latitude and longitude
* **Reverse Geocoding**: find the nearest address to coordinates

"""

import requests
import functools
import base64
import hmac
import hashlib
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from pygeolib import GeocoderError, GeocoderResult
from __version__ import VERSION

try:
    import json
except ImportError:
    import simplejson as json

__all__ = ['Geocoder', 'GeocoderError', 'GeocoderResult']


# this decorator lets me use methods as both static and instance methods
class omnimethod(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return functools.partial(self.func, instance)


class Geocoder(object):
    """
    A Python wrapper for Google Geocoding V3's API

    """

    GEOCODE_QUERY_URL = 'https://maps.google.com/maps/api/geocode/json?'
    USER_AGENT = 'pygeocoder/' + VERSION + ' (Python)'

    def __init__(self, api_key=None, client_id=None, private_key=None):
        """
        Create a new :class:`Geocoder` object using the given `client_id` and
        `private_key`.

        :param api_key: Google Maps Simple API key
        :type api_key: string

        :param client_id: Google Maps Premier client ID
        :type client_id: string

        :param private_key: Google Maps Premier API key
        :type client_id: string

        Google Maps API Premier users can provide his key to make 100,000
        requests a day vs the standard 2,500 requests a day without a key

        """
        self.api_key = api_key
        self.client_id = client_id
        self.private_key = private_key
        self.proxy = None

    @omnimethod
    def geocode(
        self,
        address,
        sensor='false',
        bounds='',
        region='',
        language='',
        components=''):
        """
        Given a string address, return a dictionary of information about
        that location, including its latitude and longitude.

        :param address: Address of location to be geocoded.
        :type address: string
        :param sensor: ``'true'`` if the address is coming from, say, a GPS device.
        :type sensor: string
        :param bounds: The bounding box of the viewport within which to bias geocode results more prominently.
        :type bounds: string
        :param region: The region code, specified as a ccTLD ("top-level domain") two-character value for biasing
        :type region: string
        :param components: The components to use when restricting the search results.
        :type components: string
        :param language: The language in which to return results.
        :type language: string
        :returns: `geocoder return value`_ dictionary
        :rtype: dict
        :raises GeocoderError: if there is something wrong with the query.

        For details on the input parameters, visit
        http://code.google.com/apis/maps/documentation/geocoding/#GeocodingRequests

        For details on the output, visit
        http://code.google.com/apis/maps/documentation/geocoding/#GeocodingResponses

        """

        params = {
            'address':  address,
            'sensor':   sensor,
            'bounds':   bounds,
            'region':   region,
            'language': language,
            'components': components,
        }

        if self is not None:
            return GeocoderResult(self.get_data(params=params))
        else:
            return GeocoderResult(Geocoder.get_data(params=params))

    @omnimethod
    def reverse_geocode(self, lat, lng, sensor='false', bounds='', region='', language=''):
        """
        Converts a (latitude, longitude) pair to an address.

        :param lat: latitude
        :type lat: float
        :param lng: longitude
        :type lng: float
        :return: `Reverse geocoder return value`_ dictionary giving closest
            address(es) to `(lat, lng)`
        :rtype: dict
        :raises GeocoderError: If the coordinates could not be reverse geocoded.

        Keyword arguments and return value are identical to those of :meth:`geocode()`.

        For details on the input parameters, visit
        http://code.google.com/apis/maps/documentation/geocoding/#GeocodingRequests

        For details on the output, visit
        http://code.google.com/apis/maps/documentation/geocoding/#ReverseGeocoding

        """
        params = {
            'latlng':   "%f,%f" % (lat, lng),
            'sensor':   sensor,
            'bounds':   bounds,
            'region':   region,
            'language': language,
        }

        if self is not None:
            return GeocoderResult(self.get_data(params=params))
        else:
            return GeocoderResult(Geocoder.get_data(params=params))

    def set_proxy(self, proxy):
        """
        Makes every HTTP request to Google geocoding server use the supplied proxy
        :param proxy: Proxy server string. Can be in the form "10.0.0.1:5000".
        :type proxy: string
        """
        self.proxy = proxy

    @omnimethod
    def get_data(self, params={}):
        """
        Retrieve a JSON object from a (parameterized) URL.

        :param params: Dictionary mapping (string) query parameters to values
        :type params: dict
        :return: JSON object with the data fetched from that URL as a JSON-format object.
        :rtype: (dict or array)

        """
        request = requests.Request(
            'GET',
            url=Geocoder.GEOCODE_QUERY_URL,
            params=params,
            headers={
                'User-Agent': Geocoder.USER_AGENT
            })

        if self and self.client_id and self.private_key:
            request = self.add_signature(request)
        elif self and self.api_key:
            request.params['key'] = self.api_key

        session = requests.Session()

        if self and self.proxy:
            session.proxies = {'https': self.proxy}

        response = session.send(request.prepare())
        session.close()

        if response.status_code == 403:
            raise GeocoderError("Forbidden, 403", response.url)
        response_json = response.json()

        if response_json['status'] != GeocoderError.G_GEO_OK:
            raise GeocoderError(response_json['status'], response.url)
        return response_json['results']

    def add_signature(self, request):
        """
        Add the client_id and signature parameters to the URL
        Based on http://gmaps-samples.googlecode.com/svn/trunk/urlsigning/urlsigner.py
        See https://developers.google.com/maps/documentation/business/webservices/auth#signature_examples
        :return: requests.Request object of type 'GET'
        """
        inputStr = request.prepare().url + '&client=' + self.client_id
        url = urlparse(inputStr)
        urlToSign = url.path + "?" + url.query
        decodedKey = base64.urlsafe_b64decode(self.private_key)
        signature = hmac.new(
            decodedKey,
            urlToSign.encode('utf-8'),
            hashlib.sha1)
        encodedSignature = base64.urlsafe_b64encode(signature.digest())
        urlSigned = inputStr + '&signature=' + encodedSignature.decode('utf-8')
        return requests.Request(
            'GET',
            url=urlSigned,
            headers={
                'User-Agent': Geocoder.USER_AGENT
            })


if __name__ == "__main__":
    import sys
    from optparse import OptionParser

    def main():
        """
        Geocodes a location given on the command line.

        Usage:
            pygeocoder.py "1600 amphitheatre mountain view ca" [YOUR_API_KEY]
            pygeocoder.py 37.4219720,-122.0841430 [YOUR_API_KEY]

        When providing a latitude and longitude on the command line, ensure
        they are separated by a comma and no space.

        """
        usage = "usage: %prog [options] address"
        parser = OptionParser(usage, version=VERSION)
        parser.add_option("-k", "--key", dest="key", help="Your Google Maps API key")
        (options, args) = parser.parse_args()

        if len(args) != 1:
            parser.print_usage()
            sys.exit(1)

        query = args[0]
        gcoder = Geocoder(options.key)

        try:
            result = gcoder.geocode(query)
        except GeocoderError as err:
            sys.stderr.write('%s\n%s\nResponse:\n' % (err.url, err))
            json.dump(err.response, sys.stderr, indent=4)
            sys.exit(1)

        print(result)
        print(result.coordinates)
    main()
