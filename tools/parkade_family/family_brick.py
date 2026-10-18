"""Finite original Urban Brick signature, fixed 54 x 36 m, five levels."""
SPEC=dict(key='brick',slug='parkade-urban-brick',label='Urban Brick Parkade',width=54,depth=36,levels=5,courtyard=None,
    description='Warm masonry piers, recessed permeable metal screens and a sheltered pedestrian entrance.')
PALETTE=dict(brick=(.44,.22,.13),mortar=(.48,.41,.32))


def extra_geometry(ctx):
    import clay_core as C
    import build as P
    front=ctx['frontY'];top=ctx['top']
    # Masonry is carried by concrete piers; actual recessed gaps stay open.
    for x in ctx['frontColumns']:
        C.box('Brick-faced structural pier',(x,front+.23,(top+1.1+.15)/2),(.85,.46,top+1.1-.15),'brick','masonry piers',0)
        for z in [.8+i*.45 for i in range(int((top+.3)/.45))]:
            C.box('Recessed masonry bed joint',(x,front-.003,z),(.85,.012,.022),'mortar','masonry detail',0)
    for z in ctx['datums'][1:]:
        C.box('Front masonry spandrel',(0,front+.1,z-.30),(44.2,.20,.43),'brick','masonry spandrels',0)
        for a,b in zip(ctx['frontColumns'],ctx['frontColumns'][1:]):
            for i in range(12):
                x=a+.55+i*(b-a-1.1)/11
                C.box('Recessed ventilation fin',(x,front+.48,z+1.25),(.06,.16,1.65),'steel','permeable screens',0)
            for h in (.43,2.08):C.box('Screen seated rail',((a+b)/2,front+.48,z+h),(b-a-.85,.16,.06),'steel','permeable screens',0)
    # Front canopy at the right stair entrance, carried by two posts.
    cx=24.5
    C.box('Pedestrian shelter roof',(cx,front+.60,2.8),(4.7,1.15,.18),'steel','pedestrian entrance',0)
    for x in (cx-2.15,cx+2.15):C.box('Canopy ground-bearing post',(x,front+.1,1.43),(.10,.10,2.56),'steel','pedestrian entrance',0)
    P.text('Urban Brick identity','URBAN BRICK',(0,front-.015,top+.45),.47,'marking')
