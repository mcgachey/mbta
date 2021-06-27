import json
import requests
import typing

import errors


class Route(object):
    """
    Model object representing a route in the MBTA API.
    """
    # Attributes to request from the API. We want this to be the minimum set of fields that we'll need to reduce
    # network cost
    fields = ['color', 'text_color', 'long_name', 'sort_order', 'type', 'direction_destinations']

    def __init__(self, record: dict):
        attributes = record.get('attributes', {})
        self.route_id = record.get('id')
        self.color = attributes.get('color', '000000')
        self.text_color = attributes.get('text_color', 'FFFFFF')
        self.long_name = attributes.get('long_name')
        self.sort_order = attributes.get('sort_order', 0)
        self.destinations = attributes.get('direction_destinations', [])
        self.type = {
            0: 'Light Rail',
            1: 'Heavy Rail',
            2: 'Commuter Rail',
            3: 'Bus',
            4: 'Ferry',
            5: 'Unknown',
        }.get(attributes.get('type', 5))


class Stop(object):
    """
    Model object representing a stop in the MBTA API.
    """
    # Attributes to request from the API. We want this to be the minimum set of fields that we'll need
    fields = [
        'address',
        'latitude',
        'longitude',
        'name',
        'platform_name',
    ]

    def __init__(self, record: dict):
        attributes = record.get('attributes', {})
        self.stop_id = record.get('id')
        self.address = attributes.get('address', '')
        self.latitude = attributes.get('latitude')
        self.longitude = attributes.get('longitude')
        self.name = attributes.get('name')
        self.platform_name = attributes.get('platform_name', '')


class MbtaApi(object):
    def __init__(self, api_key: str):
        self._api_key = api_key

    def routes(self, route_type=None) -> typing.List[Route]:
        """
        Get a list of all routes from the API. This method handles pagination.

        :return: a list of Route objects
        :raise UnexpectedServerResponseException: If the server did not respond with the expected status code.
        """
        return self._all_pages(
            url='https://api-v3.mbta.com/routes',
            query_params={
                'fields[route]': ','.join(Route.fields),
                'filter[type]': route_type
            },
            model=Route,
        )

    def route(self, route_id) -> Route:
        """
        Get data for a single route from the API.

        :return: a route object for the requested route
        :raise UnexpectedServerResponseException: If the server did not respond with the expected status code.
        """
        route_data = self._get(
            url=f"https://api-v3.mbta.com/routes/{route_id}",
            query_params={
                'fields[route]': ','.join(Route.fields),
            },
        )
        return Route(route_data.get('data', {}))

    def stops(self, route_id: str) -> typing.List[Stop]:
        """
        Get a list of all routes from the API. This method handles pagination.

        :return: a list of Stop objects
        :raise UnexpectedServerResponseException: If the server did not respond with the expected status code.
        """
        return self._all_pages(
            url='https://api-v3.mbta.com/stops',
            query_params={
                'filter[route]': route_id,
                'fields[stop]': ','.join(Stop.fields)
            },
            model=Stop,
        )

    def _all_pages(self, url: str, query_params: dict, model: typing.Type) -> typing.List:
        """
        Helper method to iterate through all pages of an endpoint. It looks like the API returns all records by default
        for the endpoints we're using, but who knows if that could change in the future.

        :param url: The full API path to fetch data
        :param query_params: Request-specific query parameters. Standard metadata such as the API key and cache control
                             are added automatically.
        :param model: A class type that will be used to construct one instance for each record retrieved
        :return: a list of model instances returned by the server, potentially across multiple pages
        :raise UnexpectedServerResponseException: If the server did not respond with the expected status code.
        """
        response_body = self._get(
            url=url,
            query_params={**{
                'page[limit]': 9999999,  # In other words, whatever the maximum number the server will give us.
                'page[offset]': 0,  # Should go without saying, but it doesn't hurt to be explicit
            }, **query_params},
        )
        records = [model(record) for record in response_body.get('data', [])]

        # If there are more results, the links.next property contains the URL for the next page. If there are no more
        # results it won't be present in the result.
        next_link = response_body.get('links', {}).get('next')
        while next_link:
            response_body = self._get(url=next_link)
            records += [model(record) for record in response_body.get('data', [])]
            next_link = response_body.get('links', {}).get('next')

        return records

    def _get(self, url: str, query_params: dict = None, expected_status=200) -> dict:
        """
        Helper method to execute a request on the server. This method adds the API key and requests a compressed payload
        to cut down on network traffic.

        :param url: The full API path to fetch data
        :param query_params: Request-specific query parameters. Standard metadata such as the API key and cache control
                             are added automatically.
        :param expected_status: The HTTP status to be returned by the server on a successful call. For the MBTA API
                                this will generally be 200 unless cache control headers are being used
        :return: the JSON data returned by a successful API call
        :raise UnexpectedServerResponseException: If the server did not respond with the expected status code.
        """
        response = requests.get(
            url,
            params={**{
                'api_key': self._api_key,
            }, **(query_params if query_params else {})},
            headers={
                'Accept-Encoding': 'gzip'
            }
        )
        if response.status_code == expected_status:
            return response.json()
        raise errors.UnexpectedServerResponseException(response)
