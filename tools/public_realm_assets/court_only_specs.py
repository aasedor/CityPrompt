"""Finite, independent native-size courts for assembling student athletic parks."""
from copy import deepcopy
from court_specs import COURTS

COURT_ONLY_KINDS = ('basketball', 'tennis', 'pickleball', 'beach_volleyball')
TITLES = {'basketball': 'Basketball court only', 'tennis': 'Tennis court only',
          'pickleball': 'Pickleball court only', 'beach_volleyball': 'Beach volleyball court only'}


def court_only_recipe(kind):
    if kind not in COURT_ONLY_KINDS:
        raise ValueError(f'Unsupported court-only sport: {kind}')
    if kind == 'pickleball':
        r = dict(sport=kind, playing_m=[6.096, 13.4112], module_m=[10.4, 19.6],
                 court_colour=[.11, .25, .29], kitchen_m=2.1336,
                 net_center_m=.8636, net_end_m=.9144,
                 source='https://usapickleball.org/what-is-pickleball/courts-and-construction/outdoor-court-construction/')
    else:
        r = deepcopy(COURTS[kind])
    r.update(id=f'court_only_{kind}_v1', title=TITLES[kind],
             dimensions_m=list(r['module_m']), include_enclosure=False,
             source_checked='2026-10-24',
             programme='Playing surface, markings, required equipment and clear playing reserve only',
             limitations=['Planning model at native size; not a certified competition facility.',
                          'Repeat and rotate courts; never stretch their playing dimensions.'])
    if kind == 'basketball':
        r['source'] = 'https://www.venueguide.fiba.basketball/vanue-design'
        r['reserve_basis'] = '3 m sides and 4 m ends, including cantilever hoop supports outside the 2 m baseline clear zone.'
    if kind == 'pickleball':
        r['reserve_basis'] = 'Preferred 34 x 64 ft overall playing area, rounded up to 10.4 x 19.6 m.'
    if kind == 'beach_volleyball':
        r['limitations'].append('3 m ordinary free zone; net shown at 2.43 m adult men height.')
    w, d = r['module_m']
    r['clear_routes'] = [dict(a=[-w/2, -d/4], b=[-r['playing_m'][0]/2-.3, -d/4], width=1.8)]
    return r
