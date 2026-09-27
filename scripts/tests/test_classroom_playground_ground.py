import importlib.util
from pathlib import Path
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

spec=importlib.util.spec_from_file_location('playground_ground',Path(__file__).parents[1]/'prepare_classroom_playground.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_whole_site_has_one_ground_owner_and_routes_are_supported():
    plan=module.prepare()
    regions=[unary_union([Polygon(t) for t in r['triangles']]) for r in plan['ground_regions']]
    assert abs(sum(r.area for r in regions)-1368)<1e-5
    assert abs(unary_union(regions).area-1368)<1e-5
    for i,region in enumerate(regions):
        for other in regions[i+1:]:assert region.intersection(other).area<1e-6
    paved=unary_union([g for g,r in zip(regions,plan['ground_regions']) if r['material'].startswith('paving')])
    for route in plan['clear_routes']:
        for i in range(101):
            t=i/100
            assert paved.covers(Point(route['a'][0]*(1-t)+route['b'][0]*t,route['a'][1]*(1-t)+route['b'][1]*t))
