"""Bounded sports batch. Metres; X across court, Y along court, Z up.

Playing dimensions are source-based. Park footprints and landscape are original
concept designs. No competition, lighting or accessible-design certification.
"""
from copy import deepcopy

SOURCES = {
    'basketball': 'https://assets.fiba.basketball/image/upload/documents-corporate-fiba-official-rules-2024-v10a.pdf',
    'three_x_three': 'https://www.fiba.basketball/en/news/fcom-3x3-v2-q-a',
    'tennis': 'https://www.itftennis.com/media/7221/2026-rules-of-tennis-english.pdf',
    'padel': 'https://www.padelfip.com/wp-content/uploads/2025/12/FIP_Rules-of-Padel-1.pdf',
    'volleyball': 'https://www.fivb.com/wp-content/uploads/2025/01/FIVB-Volleyball_Rules2025_2028-EN-v05.pdf',
    'beach_volleyball': 'https://www.fivb.com/wp-content/uploads/2025/02/FIVB-BeachVolleyball_Rules2025_2028-EN-v01.pdf',
    'badminton': 'https://www.badmintonengland.co.uk/wp-content/uploads/2022/01/Badminton-Design-Guide.pdf',
    'netball': 'https://netball.sport/game/facilities-and-equipment/',
    'bocce': 'https://usbf.us/wp-content/uploads/2026/04/2024-CBI-PRV-English-Version-FINAL-012624.pdf',
    'petanque': 'https://petanque.nz/documents/fipjp-rules-2021-with-nz-interpretations-202508.pdf',
}

def spec(kind, title, playing, module, colour, **extra):
    return dict(id=f'student_{kind}_garden_v1', title=title, sport=kind,
                playing_m=playing, module_m=module,
                dimensions_m=[round(module[0]+20, 3), round(module[1]+20, 3)],
                court_colour=colour, source=SOURCES[kind], source_checked='2026-09-23',
                programme='Native sports court, shaded social terrace, planted seating gardens and open pedestrian approach',
                **extra)

COURTS = {
    'basketball': spec('basketball', 'Neighbourhood Basketball Garden', [15,28], [21,36], [.11,.25,.27],
        hoop_height_m=3.05, hoops=2),
    'three_x_three': spec('three_x_three', '3 x 3 Pocket Basketball', [15,11], [19,17], [.25,.20,.12],
        hoop_height_m=3.05, hoops=1),
    'tennis': spec('tennis', 'Garden Tennis Court', [10.97,23.77], [18.3,36.6], [.13,.23,.27],
        singles_width_m=8.23, net_center_m=.914, net_end_m=1.07, service_distance_m=6.4),
    'padel': spec('padel', 'Glasshouse Padel Garden', [10,20], [12,22], [.10,.24,.225],
        net_center_m=.88, net_end_m=.92, service_distance_m=6.95),
    'volleyball': spec('volleyball', 'Community Volleyball Court', [9,18], [15,24], [.31,.19,.13],
        net_center_m=2.43, net_end_m=2.43, attack_line_m=3),
    'beach_volleyball': spec('beach_volleyball', 'Beach Volleyball Grove', [8,16], [14,22], [.62,.51,.32],
        net_center_m=2.43, net_end_m=2.43),
    'badminton': spec('badminton', 'Sheltered Badminton Garden', [6.1,13.4], [10.1,17.4], [.17,.28,.20],
        singles_width_m=5.18, net_center_m=1.524, net_end_m=1.55, service_distance_m=1.98),
    'netball': spec('netball', 'Neighbourhood Netball Court', [15.25,30.5], [21.35,36.6], [.22,.20,.29],
        hoop_height_m=3.05, hoops=2, goal_circle_radius_m=4.9),
    'bocce': spec('bocce', 'Bocce Pergola Garden', [4,26.5], [6.4,29], [.47,.39,.24], lanes=1),
    'petanque': spec('petanque', 'Petanque Social Gardens', [4,15], [12,19], [.47,.43,.34], lanes=2),
}

def recipe(kind):
    r=deepcopy(COURTS[kind])
    r['limitations']=[
        'Neighbourhood ideation model; not a certified competition or engineering design.',
        'Rigid court and equipment remain native size; never stretch or crop to a site polygon.',
        'Level preview only; terrain, access, edit/recovery and capture await runtime integration.',
    ]
    if kind=='badminton': r['limitations'].append('Outdoor recreational badminton in calm weather; not an indoor or AirBadminton regulation facility.')
    if kind in ('volleyball','beach_volleyball'): r['limitations'].append('Net shown at 2.43 m adult men height; other age/group heights require an equipment variant.')
    if kind=='padel': r['limitations'].append('No out-of-court play or glass structural design approval; inspect transparent rendering during later browser trial.')
    if kind=='bocce': r['limitations'].append('Sideboard access leaf shown open for arrival; close the leaf before play.')
    return r
