import json
import os
import responses
import unittest

import mbta


class RouteTestCase(unittest.TestCase):
    def __init__(self, methodname):
        super().__init__(methodname)
        self.api_key = 'API_KEY'
        self.mbta = mbta.MbtaApi(api_key=self.api_key)

    @responses.activate
    def test_basic_routes(self):
        test_data = _read_test_data('routes_response_basic.json')
        responses.add(responses.GET, 'https://api-v3.mbta.com/routes', json=test_data, status=200)

        routes = self.mbta.routes()
        assert len(test_data['data']) == len(routes)
        for i in range(len(routes)):
            _assert_route(routes[i], test_data['data'][i])

    @responses.activate
    def test_paginated_routes(self):
        page1 = _read_test_data('routes_response_paginated_1.json')
        page2 = _read_test_data('routes_response_paginated_2.json')
        responses.add(responses.GET, 'https://api-v3.mbta.com/routes', json=page1, status=200)
        responses.add(responses.GET, page1['links']['next'], json=page2, status=200)

        routes = self.mbta.routes()
        test_data = page1['data'] + page2['data']
        assert len(test_data) == len(routes)
        for i in range(len(routes)):
            _assert_route(routes[i], test_data[i])

    @responses.activate
    def test_missing_fields(self):
        test_data = _read_test_data('routes_response_missing_fields.json')
        responses.add(responses.GET, 'https://api-v3.mbta.com/routes', json=test_data, status=200)
        routes = self.mbta.routes()
        for i in range(len(routes)):
            _assert_route(routes[i], {
                'id': test_data['data'][i]['id'],
                'attributes': {
                    'color': '000000',
                    'text_color': 'FFFFFF',
                    'long_name': None,
                    'sort_order': 0
                }
            })

    @responses.activate
    def test_unexpected_server_response(self):
        test_data = _read_test_data('internal_server_error_response.json')
        responses.add(responses.GET, 'https://api-v3.mbta.com/routes', json=test_data, status=500)
        with self.assertRaises(mbta.UnexpectedServerResponseException):
            try:
                routes = self.mbta.routes()
            except mbta.UnexpectedServerResponseException as err:
                assert err.status_code == 500
                raise


def _read_test_data(filename: str):
    current_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(f"{current_dir}/test_data/{filename}", encoding='utf-8') as f:
        return json.load(f)


def _assert_route(route: mbta.Route, expected: dict):
    assert route.color == expected['attributes']['color']
    assert route.text_color == expected['attributes']['text_color']
    assert route.long_name == expected['attributes']['long_name']
    assert route.sort_order == expected['attributes']['sort_order']
    assert route.route_id == expected['id']


if __name__ == "__main__":
    unittest.main()
