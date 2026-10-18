"""Metric plan operations for the finite authored parkade assemblies."""
import math


def partition(rect, holes):
    """Disjoint rectangular difference; preserves actual voids at boundaries."""
    pieces=[tuple(rect)]
    for hole in holes:
        remaining=[]
        for a,b,c,d in pieces:
            x0,x1=max(a,hole[0]),min(b,hole[1])
            y0,y1=max(c,hole[2]),min(d,hole[3])
            if x0>=x1 or y0>=y1:
                remaining.append((a,b,c,d));continue
            for p in [(a,x0,c,d),(x1,b,c,d),(x0,x1,c,y0),(x0,x1,y1,d)]:
                if p[1]-p[0]>1e-8 and p[3]-p[2]>1e-8:remaining.append(p)
        pieces=remaining
    return pieces


def frame_plan(width,depth,levels):
    if width<50 or depth<36 or levels not in (4,5):raise ValueError('Outside finite native frame envelope')
    columns=[x for x in range(-60,61,6) if abs(x)<=width/2-5.2]
    datums=[.15+i*3.3 for i in range(levels)]
    return dict(width=width,depth=depth,levels=levels,datums=datums,top=datums[-1],
        towerHeight=datums[-1]+2.75,frontY=-depth/2,rearY=depth/2,
        rampY=(depth/2-6.45,depth/2-.05),rampX=(-width/2+7,width/2-7),
        entryX=min(columns)+3,frontColumns=columns)
