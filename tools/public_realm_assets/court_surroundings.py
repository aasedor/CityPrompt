"""Sport-specific surroundings without changing the measured court reserve."""
import math
import scene as S
import sports_furniture as F

def furnish(r):
    profile=r['reference_profile'];mw,md=r['module_m'];cy=2;front=cy-md/2;ty=front-6
    put=lambda kind,x,y,yaw=0:F.place(r,kind,x,y,yaw)
    terrace=profile['terrace']
    if terrace=='arbour':
        put('vine_pergola',0,ty)
        for x in (-2.05,2.05):put('cafe_table_chairs',x,ty)
        put('festoon_lights',0,ty-1.6)
    elif terrace=='cafe':
        for x in (-2.1,2.1):put('cafe_table_chairs',x,ty)
        put('festoon_lights',0,ty+1.45)
    elif terrace=='parasols':
        for x in (-3.5,3.5):put('cafe_parasol',x,ty)
    elif terrace=='covered':
        for x in (-3,3):put('covered_player_bench',x,ty,math.pi)
    elif terrace in ('team','club','garden'):
        put('covered_player_bench',-3,ty,math.pi)
        put({'team':'player_bench','club':'cafe_parasol','garden':'cafe_table_chairs'}[terrace],3.2,ty)
    else:
        for x in (-2.6,2.6):put('player_bench',x,ty)

    # Side amenities occupy paved alcoves beyond the full sport reserve. Keep
    # the original west arrival route open and retain the planted bed envelopes.
    for side in (-1,1):
        sx=side*(mw/2+3.6)
        S.SURFACES.append(dict(x=sx,y=cy,width=1.9,depth=min(md,15),material='paving'))
        if side==1 and profile['sideline']=='bleachers':
            put('spectator_bleachers',mw/2+3.0,cy+3.9 if profile.get('referee') else cy,-math.pi/2)
        else:
            kind='timber_seat_wall' if profile['sideline']=='walls' else 'player_bench'
            for yy in (-4.4,4.4):put(kind,sx,cy+yy,math.copysign(math.pi/2,-side))
    if profile.get('referee'):put('referee_stand',mw/2+3.6,cy,-math.pi/2)
    for x in (-mw/2-2.8,mw/2+2.8):
        for y in (front-3,cy+md/2+2.6):
            if profile['lights']=='court':put('court_floodlight',x,y)
            else:S.kit('light',x,y)
    S.kit('bike_rack',5.4,front-9.2);S.kit('bin',-5.4,ty)
    S.kit('picnic_table',-5.4,front-9.2)
