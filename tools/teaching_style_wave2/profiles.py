"""Finite native curves for the exact pavilion; no Blender dependency."""
import math


def cusped_arch_curve(width, spring, apex, samples_per_lobe=8):
    """Left spring to crown to right spring, with six rounded cusps per half.

    Dimensions follow the source silhouette. This is a discrete construction
    profile, not a surveyed historic moulding or a generic arch taxonomy.
    """
    if width <= 0 or apex <= spring or samples_per_lobe < 2:
        raise ValueError('Arch needs positive width/rise and at least two samples per lobe')
    radius=width/2;rise=apex-spring
    anchors=[(-radius*x,spring+rise*z) for x,z in
             [(1,0),(.99,.24),(.84,.43),(.61,.62),(.36,.77),(.12,.88),(0,1)]]
    left=[]
    for index,(a,b) in enumerate(zip(anchors,anchors[1:])):
        dx=b[0]-a[0];dz=b[1]-a[1];length=math.hypot(dx,dz)
        bulge=width*(.033 if index < 5 else .018)
        control=((a[0]+b[0])/2+dz/length*bulge,
                 (a[1]+b[1])/2-dx/length*bulge)
        for j in range(samples_per_lobe):
            t=j/samples_per_lobe
            left.append(((1-t)**2*a[0]+2*(1-t)*t*control[0]+t*t*b[0],
                         (1-t)**2*a[1]+2*(1-t)*t*control[1]+t*t*b[1]))
    left.append((0,apex))
    return left+[(-u,z) for u,z in reversed(left[:-1])]
