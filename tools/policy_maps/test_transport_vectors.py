import unittest
from fetch_transport_vectors import normalize_feature, group_routes


class TransportVectorTests(unittest.TestCase):
    def test_grouping_preserves_all_line_coordinates_and_priority(self):
        features = {}
        for identity, priority, geometry in [
            ('a', 'PRIMARY', {'type': 'LineString', 'coordinates': [[-114.1, 51.1], [-114.2, 51.2]]}),
            ('b', 'PRIMARY', {'type': 'MultiLineString', 'coordinates': [[[-114.3, 51.3], [-114.4, 51.4]]]}),
            ('c', 'SECONDARY', {'type': 'LineString', 'coordinates': [[-114.5, 51.5], [-114.6, 51.6]]}),
        ]:
            features[identity] = normalize_feature({'properties': {'GLOBALID': identity, 'CLASS_5A': 'PROPOSED PATHWAY',
                'PRIORITY_5A': priority}, 'geometry': geometry}, '5a', 'city')
        groups = group_routes(features)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups['proposed-pathway:PRIMARY:city']['geometry']['coordinates'],
                         [features['a']['geometry']['coordinates'], *features['b']['geometry']['coordinates']])
        self.assertEqual(groups['proposed-pathway:SECONDARY:city']['geometry']['coordinates'],
                         [features['c']['geometry']['coordinates']])

    def test_preserves_official_coordinates_class_and_stable_id(self):
        row = {'geometry': {'type': 'MultiLineString', 'coordinates': [[[-114.1, 51.1], [-114.2, 51.2]]]},
               'properties': {'GLOBALID': 'abc', 'CLASS_5A': 'PROPOSED PATHWAY', 'PRIORITY_5A': 'PRIMARY'}}
        out = normalize_feature(row, '5a', 'source')
        self.assertEqual(out['geometry'], row['geometry'])
        self.assertEqual(out['id'], 'abc')
        self.assertEqual(out['properties']['category'], 'proposed-pathway')
        self.assertEqual(out['properties']['priority'], 'PRIMARY')

    def test_rejects_unknown_designation_and_invalid_geometry(self):
        row = {'geometry': {'type': 'Point', 'coordinates': [-114, 51]},
               'properties': {'description': 'New unknown designation', 'globalid': 'abc'}}
        with self.assertRaises(ValueError): normalize_feature(row, 'transit', 'source')
        row['properties']['description'] = 'Primary Transit Hub'
        row['geometry'] = None
        with self.assertRaises(ValueError): normalize_feature(row, 'transit', 'source')


if __name__ == '__main__': unittest.main()
