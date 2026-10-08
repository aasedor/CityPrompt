import unittest
from fetch_transit_service import build_snapshots


class TransitServiceTests(unittest.TestCase):
    def test_keeps_route_identity_and_joins_all_routes_to_active_stops(self):
        route = {'globalid': 'route-a', 'route_category': 'REGULAR', 'route_short_name': '7',
                 'route_long_name': 'Marda Loop', 'multilinestring': {'type': 'MultiLineString', 'coordinates': [[[-114.1, 51.05], [-114.11, 51.06]]]}}
        stop = {'globalid': 'stop-a', 'teleride_number': '1234', 'stop_name': 'WB Example', 'status': 'ACTIVE',
                'point': {'type': 'Point', 'coordinates': [-114.1, 51.05]}}
        refs = [{'teleride_number': '1234', 'route_short_name': '7', 'route_long_name': 'Marda Loop'},
                {'teleride_number': '1234', 'route_short_name': '9', 'route_long_name': 'Dalhousie'},
                {'teleride_number': '1234', 'route_short_name': '7', 'route_long_name': 'Marda Loop'}]
        routes, stops = build_snapshots([route], [stop, {**stop, 'globalid': 'inactive', 'status': 'INACTIVE'}], refs, {})
        self.assertEqual(routes['features'][0]['properties']['routeNumber'], '7')
        self.assertEqual(routes['features'][0]['properties']['name'], 'Marda Loop')
        self.assertEqual(routes['features'][0]['geometry'], route['multilinestring'])
        self.assertEqual(len(stops['features']), 1)
        self.assertEqual(stops['features'][0]['properties']['stopNumber'], '1234')
        self.assertEqual([r['number'] for r in stops['features'][0]['properties']['routes']], ['7', '9'])

    def test_rejects_unknown_categories_instead_of_misclassifying_routes(self):
        with self.assertRaises(ValueError):
            build_snapshots([{'route_category': 'UNREVIEWED'}], [], [], {})


if __name__ == '__main__': unittest.main()
