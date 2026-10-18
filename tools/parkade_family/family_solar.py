"""Finite Solar Ribbon signature, fixed 66 x 36 m, five levels."""
SPEC=dict(key='solar',slug='parkade-solar-ribbon',label='Solar Ribbon Parkade',width=66,depth=36,levels=5,courtyard=None,roof_lights=False,
    description='Supported metal ribbon fins, a solar roof canopy and marked EV bays; no energy or capacity claim.')
PALETTE=dict(ribbon=(.57,.62,.64),solar=(.035,.085,.13),cell=(.14,.23,.30),ev=(.12,.36,.30))


def extra_geometry(ctx):
    import clay_core as C
    import build as P
    front=ctx['frontY'];top=ctx['top']
    # Front fin ribbons terminate against continuous frame rails at each floor.
    for z in ctx['datums'][1:]:
        for x in range(-27,28,2):
            a=(x,front+.12,z+.15);b=(x+.60,front+.12,z+2.55)
            C.beam('Diagonal ribbon fin',a,b,.13,.13,'ribbon','solar ribbon screen')
        for h in (.15,2.55):C.box('Ribbon supporting rail',(0,front+.12,z+h),(56,.20,.10),'steel','solar ribbon screen',0)
    # Six metre clear parking aisles remain beneath a roof-level canopy.
    roof=top+2.45
    for x in (-24,-12,0,12,24):
        for y in (-5.75,5.75):C.box('Solar canopy load-bearing post',(x,y,(top+roof-.12)/2),(.16,.16,roof-.12-top),'steel','solar canopy',0)
        C.box('Canopy transverse beam',(x,0,roof-.10),(.18,24,.20),'steel','solar canopy',0)
    for y in (-11.9,0,11.9):C.box('Canopy longitudinal purlin',(0,y,roof-.02),(54,.10,.12),'steel','solar canopy',0)
    for i in range(18):
        for j in range(8):
            x=-25.5+i*3;y=-10.5+j*3
            C.box('Individual photovoltaic panel',(x,y,roof+.08),(2.9,2.9,.08),'solar','photovoltaic canopy',0)
            # Physical grid lines; no image textures or empty backing cards.
            for dx in (-.95,0,.95):C.box('Photovoltaic cell division',(x+dx,y,roof+.123),(.014,2.86,.005),'cell','photovoltaic detail',0)
    for x in (7,12.4,17.8):
        C.box('EV charging pedestal',(x,-.25,.85),(.35,.30,1.4),'ev','EV equipment',0)
        C.box('EV display',(x,-.407,1.12),(.22,.015,.30),'sign','EV equipment',0)
        C.rod('EV cable left',(x+.18,-.3,1.25),(x+.35,-.65,.75),.025,'steel','EV equipment',6)
        C.rod('EV cable return',(x+.35,-.65,.75),(x+.18,-.3,.5),.025,'steel','EV equipment',6)
        P.text('EV bay marking','EV',(x,-3.5,.17),.7,'ev',rotation=(0,0,0))
