"""Approved finite batch; one exact design and runtime identity per family."""
SPECS={
 'courtyard':dict(slug='final-courtyard-block',label='Brick Garden Courtyard',floors=4,group='mixed',type='mixed_use',dimensions=[30,24.4,15],entrance=[0,-13.1,3.2],
    description='Four-storey homes over shops, recessed balconies, an open pedestrian passage and a planted shared courtyard.',
    uses=[['Multi-Residential Development','Dwelling Unit'],['Retail and Consumer Service'],['Restaurant: Food Service Only']]),
 'seniors':dict(slug='final-seniors-apartments',label='Aspen Terrace Seniors Apartments',floors=5,group='apartments',type='residential_multifamily',dimensions=[32,16,17.5],entrance=[0,-8,2.5],
    description='Five-storey independent seniors apartments with three balcony columns, a shared lounge and planted garden terrace.',
    uses=[['Multi-Residential Development','Dwelling Unit']]),
 'health':dict(slug='final-health-centre',label='Neighbourhood Health Centre',floors=2,group='civic',type='institutional',dimensions=[35,22,9.1],entrance=[-1.7,-11,3.5],
    description='Two-storey clinic and pharmacy around a garden, with a covered drop-off, waiting areas and consulting rooms.',
    uses=[['Health Care Service'],['Retail and Consumer Service']]),
 'market':dict(slug='final-urban-grocery',label='Sawtooth Neighbourhood Grocery',floors=1,group='shops',type='commercial_retail',dimensions=[20,14.2,7.1],entrance=[0,-6,2.5],
    description='A compact urban supermarket with four roof lanterns, a transparent storefront, stocked aisles and a covered entrance.',
    uses=[['Retail and Consumer Service']]),
 'transit':dict(slug='final-transit-pavilion',label='Timber Wing Transit Pavilion',floors=1,group='infrastructure',type='institutional',dimensions=[28,13,6.8],entrance=[0,-6.5,3],
    description='A glazed waiting hall with four timber V-columns, an asymmetric canopy, ticket machines and a small cafe. Tracks are separate.',
    uses=[['Restaurant: Food Service Only']]),
}
