import sys
import collections


class GeocoderResult(collections.Iterator):
    """
    A geocoder resultset to iterate through address results.
    Exemple:

    results = Geocoder.geocode('paris, us')
    for result in results:
        print(result.formatted_address, result.location)

    Provide shortcut to ease field retrieval, looking at 'types' in each
    'address_components'.
    Example:
        result.country
        result.postal_code

    You can also choose a different property to display for each lookup type.
    Example:
        result.country__short_name

    By default, use 'long_name' property of lookup type, so:
        result.country
    and:
        result.country__long_name
    are equivalent.
    """

    attribute_mapping = {
        "state": "administrative_area_level_1",
        "province": "administrative_area_level_1",
        "city": "locality",
        "county": "administrative_area_level_2",
    }

    def __init__(self, data):
        """
        Creates instance of GeocoderResult from the provided JSON data array
        """
        self.data = data
        self.len = len(self.data)
        self.current_index = 0
        self.current_data = self.data[0]

    def __len__(self):
        return self.len

    def __iter__(self):
        return self

    def return_next(self):
        if self.current_index >= self.len:
            raise StopIteration
        self.current_data = self.data[self.current_index]
        self.current_index += 1
        return self

    def __getitem__(self, key):
        """
        Accessing GeocoderResult by index will return a GeocoderResult
        with just one data entry
        """
        return GeocoderResult([self.data[key]])

    def __unicode__(self):
        return self.formatted_address

    if sys.version_info[0] >= 3:  # Python 3
        def __str__(self):
            return self.__unicode__()

        def __next__(self):
            return self.return_next()
    else:  # Python 2
        def __str__(self):
            return self.__unicode__().encode('utf8')

        def next(self):
            return self.return_next()

    @property
    def count(self):
        return self.len

    @property
    def coordinates(self):
        """
        Return a (latitude, longitude) coordinate pair of the current result
        """
        location = self.current_data['geometry']['location']
        return location['lat'], location['lng']

    @property
    def location_type(self):
        """
        Return location type for current result
        """
        return self.current_data['geometry']['location_type']

    @property
    def latitude(self):
        return self.coordinates[0]

    @property
    def longitude(self):
        return self.coordinates[1]

    @property
    def raw(self):
        """
        Returns the full result set in dictionary format
        """
        return self.data

    @property
    def valid_address(self):
        """
        Returns true if queried address is valid street address
        """
        return self.current_data['types'] == [u'street_address']

    @property
    def formatted_address(self):
        return self.current_data['formatted_address']

    def __getattr__(self, name):
        lookup = name.split('__')
        attribute = lookup[0]

        if (attribute in GeocoderResult.attribute_mapping):
            attribute = GeocoderResult.attribute_mapping[attribute]

        try:
            prop = lookup[1]
        except IndexError:
            prop = 'long_name'

        for elem in self.current_data['address_components']:
            if attribute in elem['types']:
                return elem[prop]


class GeocoderError(Exception):
    """Base class for errors in the :mod:`pygeocoder` module.

    Methods of the :class:`Geocoder` raise this when something goes wrong.

    """
    #: See http://code.google.com/apis/maps/documentation/geocoding/index.html#StatusCodes
    #: for information on the meaning of these status codes.
    G_GEO_OK = "OK"
    G_GEO_ZERO_RESULTS = "ZERO_RESULTS"
    G_GEO_OVER_QUERY_LIMIT = "OVER_QUERY_LIMIT"
    G_GEO_REQUEST_DENIED = "REQUEST_DENIED"
    G_GEO_MISSING_QUERY = "INVALID_REQUEST"

    def __init__(self, status, url=None, response=None):
        """Create an exception with a status and optional full response.

        :param status: Either a ``G_GEO_`` code or a string explaining the
         exception.
        :type status: int or string
        :param url: The query URL that resulted in the error, if any.
        :type url: string
        :param response: The actual response returned from Google, if any.
        :type response: dict

        """
        Exception.__init__(self, status) # Exception is an old-school class
        self.status = status
        self.url = url
        self.response = response

    def __str__(self):
        """Return a string representation of this :exc:`GeocoderError`."""
        return 'Error %s\nQuery: %s' % (self.status, self.url)

    def __unicode__(self):
        """Return a unicode representation of this :exc:`GeocoderError`."""
        return unicode(self.__str__())
