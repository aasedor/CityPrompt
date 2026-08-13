"""Construction-locked Peranakan shophouse row: six or seven atomic units."""
from __future__ import annotations
import hashlib,json,math
from typing import Any
ARCHETYPE_ID="shophouse_southeast_asian";VARIANT_ID="shophouse_peranakan";UW=5.;D=28.;TD=1.7
SIZES={"canonical":(6,30.),"extended":(7,35.)};REFS=[f"frontend/public/archetypes/buildings/shophouse_southeast_asian/variant_0{x}" for x in (".png","_angle_60.jpg","_angle_90.jpg")]
COLORS=["turquoise_plaster","turquoise_plaster","coral_plaster","ochre_plaster","mint_plaster","lavender_plaster","cream_plaster"]
TEMPLATES=("floral_panel","pilaster_capital","shuttered_bay","tile_dado_balcony")
def digest(v:Any):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def mesh(n,v,f,o,d,**m):return {"name":n,"vertices":v,"faces":f,"face_owners":[[o] for _ in f],"sticker_owner_id":o,"material_domain":d,"face_roles":[d]*len(f),**m}
def box(n,b,o,d,**m):
 x0,x1,y0,y1,z0,z1=b;v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
 return mesh(n,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],o,d,closed=True,outward_winding=True,cap_faces=[2,3,4,5],**m)
def relief_prism(n,outline,y0,y1,o,d,**m):
 count=len(outline);v=[[x,y0,z] for x,z in outline]+[[x,y1,z] for x,z in outline]
 f=[list(range(count)),list(reversed(range(count,2*count)))]+[[i,(i+1)%count,(i+1)%count+count,i+count] for i in range(count)]
 return mesh(n,v,f,o,d,closed=True,outward_winding=True,shaped_relief=True,**m)
def lobed_outline(cx,cz,rx,rz,lobes=6,steps=24):
 return [(cx+rx*(.74+.26*math.cos(lobes*a))*math.cos(a),cz+rz*(.74+.26*math.cos(lobes*a))*math.sin(a)) for a in (2*math.pi*i/steps for i in range(steps))]
def arch_points(x,z0=4.7,s=7.,r=.62):return [(x-r,z0),(x+r,z0),(x+r,s)]+[(x+r*math.cos(i*math.pi/12),s+r*math.sin(i*math.pi/12)) for i in range(1,13)]
def arch_plane(name,pts,y,owner,domain,**metadata):
 vs=[[a,y,z] for a,z in pts];ci=len(vs);cx=sum(a for a,_ in pts)/len(pts);cz=sum(z for _,z in pts)/len(pts);vs.append([cx,y,cz])
 faces=[[ci,i,(i+1)%len(pts)] for i in range(len(pts))]
 return mesh(name,vs,faces,owner,domain,contour_aware=True,**metadata)
def arch_assembly(u,b,x,xlo,xhi,domain):
 p=f"unit_{u}_arch_{b}";pts=arch_points(x);z0=4.25;zt=8.2;left=x-.62;right=x+.62;ms=[]
 # Wall panels stop at aperture: side strips, sill panel, and 12 closed chord-to-top tiles.
 if xlo<left:ms.append(box(p+"_wall_left",(xlo,left,-D/2+.12,-D/2+.52,z0,zt),"sticker_"+p+"_wall",domain,carrier_kind="arch_cut_wall_panel",unit=u,bay=b))
 ms.append(box(p+"_wall_sill",(left,right,-D/2+.12,-D/2+.52,z0,4.7),"sticker_"+p+"_wall",domain,carrier_kind="arch_cut_wall_panel",unit=u,bay=b))
 for i,(a,c) in enumerate(zip(pts[2:],pts[3:])):
  ms.append(box(f"{p}_wall_head_{i}",(min(a[0],c[0]),max(a[0],c[0]),-D/2+.12,-D/2+.52,max(a[1],c[1]),zt),"sticker_"+p+"_wall",domain,carrier_kind="arch_cut_wall_panel",unit=u,bay=b))
 if right<xhi:ms.append(box(p+"_wall_right",(right,xhi,-D/2+.12,-D/2+.52,z0,zt),"sticker_"+p+"_wall",domain,carrier_kind="arch_cut_wall_panel",unit=u,bay=b))
 # Optical layers are inset from the return contour. The opaque backing uses
 # a larger but still aperture-bounded contour, preventing environment/header
 # leaks while preserving a real recessed pane and a separate interior card.
 optical_pts=arch_points(x,z0=4.82,s=7.,r=.50);backing_pts=arch_points(x,z0=4.74,s=7.,r=.58)
 glass=p+"_glass";card=p+"_card";backing=p+"_interior_backing"
 ms += [arch_plane(glass,optical_pts,-D/2+.58,"sticker_"+glass,"recessed_glazing",carrier_kind="arch_clipped_glass",unit=u,bay=b,approved_contour="optical_inset"),arch_plane(card,optical_pts,-D/2+.88,"sticker_"+card,"interior_card",carrier_kind="arch_clipped_card",unit=u,bay=b,approved_contour="optical_inset"),arch_plane(backing,backing_pts,-D/2+1.00,"sticker_"+backing,"interior_backing",carrier_kind="arch_contour_interior_backing",unit=u,bay=b,opaque=True,environment_occlusion=True,approved_contour="backing_inset",optical_margin_m=.08)]
 returns=[]
 for i,(a,c) in enumerate(zip(pts,pts[1:]+pts[:1])):
  n=f"{p}_return_{i}";returns.append(n);ms.append(mesh(n,[[a[0],-D/2+.12,a[1]],[c[0],-D/2+.12,c[1]],[c[0],-D/2+.58,c[1]],[a[0],-D/2+.58,a[1]]],[[0,1,2,3]],"sticker_"+p+"_returns","plaster_trim",carrier_kind="arched_opening_return",unit=u,bay=b))
 # Shutters/mullions are physical, shallow and aperture-bounded.
 details=[]
 for j,xx in enumerate((x-.24,x+.24)):
  n=f"{p}_mullion_{j}";details.append(n);ms.append(box(n,(xx-.025,xx+.025,-D/2+.53,-D/2+.59,4.76,7.45),"sticker_"+p+"_wood","dark_timber",carrier_kind="physical_window_mullion",unit=u,bay=b))
 for j,(a,c) in enumerate(((x-.60,x-.40),(x+.40,x+.60))):
  n=f"{p}_shutter_{j}";details.append(n);ms.append(box(n,(a,c,-D/2+.03,-D/2+.12,4.82,6.88),"sticker_"+p+"_shutters","dark_timber",carrier_kind="physical_shutter",unit=u,bay=b))
 return ms,{"unit":u,"bay":b,"glass":glass,"card":card,"backing":backing,"approved_opening_contour":pts,"optical_contour":optical_pts,"backing_contour":backing_pts,"returns":returns,"detail_meshes":details,"flat_printed":False}
def shopfront(u,x0,x1,domain,template):
 p=f"unit_{u}_shopfront";y=-D/2+TD;ms=[]
 # Split recessed door/window/transom/grille/dado; never a solid arcade back.
 configs={
  "floral_panel":((.28,1.58,"window"),(1.82,3.18,"carved_door"),(3.42,4.72,"window")),
  "pilaster_capital":((.28,1.48,"carved_door"),(1.72,3.12,"window"),(3.36,4.72,"window")),
  "shuttered_bay":((.28,1.62,"window"),(1.86,3.38,"window"),(3.62,4.72,"carved_door")),
  "tile_dado_balcony":((.28,1.38,"carved_door"),(1.62,3.38,"window"),(3.62,4.72,"carved_door")),
 }
 raw=configs[template];spans=tuple((x0+a,x0+b,k) for a,b,k in raw)
 dado=[]
 for i,(a,b,_) in enumerate(spans):
  q=f"{p}_tile_dado_{i}";dado.append(q);ms.append(box(q,(a,b,y-.16,y,.1,1.05),"sticker_"+p+"_dado","peranakan_tile",carrier_kind="tile_dado",unit=u,template=template,segment=i))
 piers=[]
 for i,(a,b) in enumerate(((spans[0][1],spans[1][0]),(spans[1][1],spans[2][0]))):
  q=f"{p}_ground_pier_{i}";piers.append(q);ms.append(box(q,(a,b,y-.12,y+.02,.1,3.98),"sticker_"+p+"_pier",domain,carrier_kind="ground_shopfront_pier",unit=u,template=template))
 openings=[]
 for i,(a,b,kind) in enumerate(spans):
  gl=f"{p}_{kind}_{i}_glass";card=f"{p}_{kind}_{i}_interior";ms.append(mesh(gl,[[a,y+.08,1.08],[b,y+.08,1.08],[b,y+.08,3.25],[a,y+.08,3.25]],[[0,1,2,3]],"sticker_"+gl,"recessed_glazing",carrier_kind="shopfront_glass",unit=u));ms.append(mesh(card,[[a,y+.35,1.08],[b,y+.35,1.08],[b,y+.35,3.25],[a,y+.35,3.25]],[[0,1,2,3]],"sticker_"+card,"interior_card",carrier_kind="shopfront_interior",unit=u))
  frames=[]
  for label,fa,fb,fz0,fz1 in (("left",a-.06,a+.02,1.,3.35),("right",b-.02,b+.06,1.,3.35),("bottom",a+.02,b-.02,1.,1.10),("top",a+.02,b-.02,3.25,3.35)):
   q=f"{p}_{kind}_{i}_frame_{label}";frames.append(q);ms.append(box(q,(fa,fb,y-.01,y+.07,fz0,fz1),"sticker_"+p+"_timber","dark_timber",carrier_kind="shopfront_perimeter_member",unit=u,opening=i))
  mullions=[]
  # Restrained 0/1 mullions keep broad shopfront panes dominant; the arcade
  # piers remain the primary vertical order rather than a picket-like curtain.
  mullion_count=1 if (template,i) in {("floral_panel",0),("pilaster_capital",1),("shuttered_bay",1),("tile_dado_balcony",1)} else 0
  for j in range(1,mullion_count+1):
   xx=a+(b-a)*j/(mullion_count+1);q=f"{p}_{kind}_{i}_mullion_{j}";mullions.append(q);ms.append(box(q,(xx-.025,xx+.025,y-.005,y+.065,1.1,3.25),"sticker_"+p+"_timber","dark_timber",carrier_kind="shopfront_mullion",unit=u,opening=i))
  carving=[]
  if kind=="carved_door":
   for j in range(3):
    q=f"{p}_opening_{i}_door_carving_{j}";carving.append(q);ms.append(box(q,(a+.18+j*.34,a+.30+j*.34,y-.08,y-.01,1.35,2.85),"sticker_"+p+f"_opening_{i}_carving","carved_timber",carrier_kind="door_carving_relief",unit=u,opening=i,carving=j))
  openings.append({"kind":kind,"glass":gl,"card":card,"frame_members":frames,"mullions":mullions,"carvings":carving})
 trans=[];grille=[]
 for i,(a,b,_) in enumerate(spans):
  tq=f"{p}_transom_{i}";trans.append(tq);ms.append(box(tq,(a,b,y-.02,y+.06,3.35,3.72),"sticker_"+p+"_timber","dark_timber",carrier_kind="shopfront_transom",unit=u,template=template,segment=i))
  for j in range(2+(u+i)%3):
   xx=a+(b-a)*(j+1)/(3+(u+i)%3);q=f"{p}_vent_grille_{i}_{j}";grille.append(q);ms.append(box(q,(xx-.02,xx+.02,y-.04,y+.04,3.72,3.98),"sticker_"+p+"_grille","dark_timber",carrier_kind="vent_grille",unit=u,template=template,segment=i))
 surrounds=[]
 if template in {"floral_panel","pilaster_capital","tile_dado_balcony"}:
  targets=(1,) if template!="tile_dado_balcony" else (0,2)
  for i in targets:
   a,b,_=spans[i]
   for label,bb in (("left",(a-.08,a,y-.10,y-.01,1.02,3.78)),("right",(b,b+.08,y-.10,y-.01,1.02,3.78)),("head",(a,b,y-.10,y-.01,3.70,3.78))):
    q=f"{p}_pale_surround_{i}_{label}";surrounds.append(q);ms.append(box(q,bb,"sticker_pale_shopfront_surround","plaster_trim",carrier_kind="selective_pale_shopfront_surround",unit=u,template=template,opening=i,does_not_close_tunnel=True))
 return ms,{"unit":u,"template":template,"openings":openings,"tile_dado":dado,"ground_piers":piers,"transom":trans,"grille":grille,"pale_surrounds":surrounds}
def pitched_roof(u,x0,x1,prefix="main",y0=-D/2,y1=D/2,z=8.25,ridge=11.):
 p=f"unit_{u}_{prefix}_roof";t=.18;ry=(y0+y1)/2;v=[[x0,y0,z],[x1,y0,z],[x1,ry,ridge],[x0,ry,ridge],[x0,y0+t,z],[x1,y0+t,z],[x1,ry,ridge-t],[x0,ry,ridge-t],[x0,ry,ridge],[x1,ry,ridge],[x1,y1,z],[x0,y1,z],[x0,ry,ridge-t],[x1,ry,ridge-t],[x1,y1-t,z],[x0,y1-t,z]]
 faces=[[0,1,2,3],[7,6,5,4],[0,4,5,1],[3,2,6,7],[0,3,7,4],[1,5,6,2],[8,9,10,11],[15,14,13,12],[8,12,13,9],[11,10,14,15],[8,11,15,12],[9,13,14,10]]
 m=mesh(p,v,faces,"sticker_"+p,"terracotta_roof",carrier_kind="closed_pitched_roof",unit=u,closed=True,outward_winding=True,eaves=True,gables=True,ridge=True,returns=True)
 m["ridge_y_m"]=ry;return m
def dormer(u,x):
 p=f"unit_{u}_louvred_dormer";base=10.62;ms=[box(p+"_frame",(x-.78,x+.78,-2.58,-2.38,base,11.17),"sticker_"+p,"painted_timber",carrier_kind="dormer_frame",unit=u,seated_above_main_roof=True,shallow_depth_m=.20)]
 for i in range(5):ms.append(box(f"{p}_louvre_{i}",(x-.61,x+.61,-2.67,-2.58,base+.06+i*.085,base+.105+i*.085),"sticker_"+p,"dark_timber",carrier_kind="dormer_louvre",unit=u,seated_above_main_roof=True,horizontal_louvre=True))
 cap=pitched_roof(u,x-.86,x+.86,"dormer_cap",-2.78,-2.18,11.17,11.45);cap["shallow_cap_depth_m"]=.60;ms.append(cap);return ms
def balcony(u,x0,x1,width):
 c=(x0+x1)/2;a=c-width/2;b=c+width/2;y0=-D/2-.92;y1=-D/2-.08;ms=[];names=[]
 slab=f"unit_{u}_balcony_slab";names.append(slab);ms.append(box(slab,(a,b,y0,y1,4.02,4.18),"sticker_balcony","plaster_trim",carrier_kind="balcony_slab",unit=u))
 for j,x in enumerate((a+.10,b-.10)):
  n=f"unit_{u}_balcony_post_{j}";names.append(n);ms.append(box(n,(x-.035,x+.035,y0-.02,y0+.05,4.18,5.12),"sticker_balcony_iron","dark_iron",carrier_kind="balcony_post",unit=u))
 top=f"unit_{u}_balcony_top_rail";names.append(top);ms.append(box(top,(a+.06,b-.06,y0-.04,y0+.06,5.08,5.16),"sticker_balcony_iron","dark_iron",carrier_kind="balcony_top_rail",unit=u))
 for j in range(9):
  x=a+.2+j*(width-.4)/8;n=f"unit_{u}_balcony_rail_{j}";names.append(n);ms.append(box(n,(x-.018,x+.018,y0-.01,y0+.035,4.22,5.08),"sticker_balcony_iron","dark_iron",carrier_kind="balcony_rail",unit=u))
 for j,x in enumerate((a+.35,b-.35)):
  n=f"unit_{u}_balcony_bracket_{j}";names.append(n);ms.append(box(n,(x-.10,x+.10,y1-.20,y1,3.65,4.03),"sticker_balcony","plaster_trim",carrier_kind="balcony_bracket",unit=u))
 for j,x in enumerate((a+.05,b-.05)):
  n=f"unit_{u}_balcony_side_return_guard_{j}";names.append(n);ms.append(box(n,(x-.035,x+.035,y0,y1,4.20,5.12),"sticker_balcony_iron","dark_iron",carrier_kind="balcony_side_return_guard",unit=u))
 return ms,{"unit":u,"width":width,"parts":names}

def template_details(u,x0,x1,template,domain):
 ms=[]
 # Four distinct topologies, not metadata-only labels.
 if template=="floral_panel":
  for j in range(5):
   cx=x0+.49+j*.83;ms.append(relief_prism(f"unit_{u}_floral_medallion_{j}",lobed_outline(cx,7.84,.20,.18),-D/2-.11,-D/2-.02,"sticker_motif","plaster_relief",carrier_kind="relief_medallion",unit=u,template=template,motif="six_lobed_flower"))
 elif template=="pilaster_capital":
  for j,x in enumerate((x0+.12,x0+1.65,x0+3.22,x1-.24)):
   ms.append(box(f"unit_{u}_pilaster_{j}",(x,x+.12,-D/2-.04,-D/2+.12,4.28,7.55),"sticker_pilaster","plaster_trim",carrier_kind="shaped_pilaster",unit=u,template=template));cx=x+.06;outline=[(cx-.22,7.48),(cx+.22,7.48),(cx+.27,7.60),(cx+.16,7.78),(cx+.08,7.86),(cx,7.80),(cx-.08,7.86),(cx-.16,7.78),(cx-.27,7.60)];ms.append(relief_prism(f"unit_{u}_shaped_capital_{j}",outline,-D/2-.12,-D/2+.01,"sticker_capital","plaster_relief",carrier_kind="shaped_capital",unit=u,template=template,motif="scrolled_capital"))
 elif template=="shuttered_bay":
  for j in range(3):
   a=x0+.26+j*1.55;b=x0+1.55+j*1.55
   # Frame terminates at the universal arch spring; a low impost rail leaves
   # the round crown entirely exposed rather than boxing it into a rectangle.
   for label,fa,fb,z0,z1 in (("left",a,a+.08,4.62,7.0),("right",b-.08,b,4.62,7.0),("sill",a+.08,b-.08,4.62,4.72),("impost",a+.08,b-.08,6.92,7.0)):
    ms.append(box(f"unit_{u}_shutter_frame_{j}_{label}",(fa,fb,-D/2-.12,-D/2+.02,z0,z1),"sticker_shutter_frame","dark_timber",carrier_kind="open_shutter_frame_member",unit=u,template=template,opening=j))
   for side,sa,sb in (("left_leaf",a+.08,a+.25),("right_leaf",b-.25,b-.08)):
    ms.append(box(f"unit_{u}_shutter_{j}_{side}",(sa,sb,-D/2-.19,-D/2-.11,4.76,7.46),"sticker_shutter","dark_timber",carrier_kind="side_shutter_leaf",unit=u,template=template,opening=j))
 else:
  for j in range(8):ms.append(box(f"unit_{u}_tile_relief_cluster_{j}",(x0+.22+j*.57,x0+.62+j*.57,-D/2-.06,-D/2+.02,4.30,4.62),"sticker_tile_relief","peranakan_tile",carrier_kind="tile_relief_cluster",unit=u,template=template))
 # Readable shallow flora/fauna occupy the spandrels and frieze. Their shaped
 # silhouettes avoid the square-cube appearance of the first clay pass.
 # Their position is invariant while the four template branches retain their
 # distinct pilaster, shutter, tile and medallion topology.
 for j,cx in enumerate((x0+1.70,x0+3.28)):
  pendant=[(cx,7.34),(cx+.13,7.46),(cx+.10,7.66),(cx+.19,7.78),(cx+.08,7.91),(cx,8.02),(cx-.08,7.91),(cx-.19,7.78),(cx-.10,7.66),(cx-.13,7.46)]
  ms.append(relief_prism(f"unit_{u}_spandrel_floral_cluster_{j}",pendant,-D/2-.13,-D/2-.02,"sticker_spandrel_flora","plaster_relief",carrier_kind="floral_motif_cluster",unit=u,template=template,shallow_relief=True,motif="hanging_floral_pendant"))
 cx=x0+2.50;bird=[(cx-.46,7.84),(cx-.25,7.95),(cx-.09,7.90),(cx,8.05),(cx+.09,7.90),(cx+.25,7.95),(cx+.46,7.84),(cx+.22,7.76),(cx+.06,7.80),(cx,7.68),(cx-.06,7.80),(cx-.22,7.76)]
 ms.append(relief_prism(f"unit_{u}_spandrel_faunal_cluster",bird,-D/2-.14,-D/2-.02,"sticker_spandrel_fauna","plaster_relief",carrier_kind="faunal_motif_cluster",unit=u,template=template,shallow_relief=True,motif="paired_bird_wings"))
 # Fine continuous fretwork/pendant rhythm below the main frieze.
 fret_count=(12,14,13,11)[u%4];spacing=4.5/(fret_count-1)
 for j in range(fret_count):
  cx=x0+.25+j*spacing;flower=lobed_outline(cx,7.79,.060,.050,lobes=5,steps=15)
  ms.append(relief_prism(f"unit_{u}_fretwork_flower_{j}",flower,-D/2-.09,-D/2-.02,"sticker_fretwork","plaster_relief",carrier_kind="continuous_fretwork_relief",unit=u,template=template,motif="small_rounded_flower_center",sequence=j,thin_band=True))
 pendant_x={"floral_panel":(1.05,2.50,3.95),"pilaster_capital":(.82,2.02,3.22,4.18),"shuttered_bay":(1.25,2.50,3.75),"tile_dado_balcony":(.92,2.50,4.08)}[template]
 for j,offset in enumerate(pendant_x):
  cx=x0+offset;drop=[(cx-.035,7.72),(cx+.035,7.72),(cx+.045,7.60),(cx,7.51),(cx-.045,7.60)]
  ms.append(relief_prism(f"unit_{u}_frieze_pendant_{j}",drop,-D/2-.10,-D/2-.02,"sticker_pendant","plaster_relief",carrier_kind="continuous_pendant_relief",unit=u,template=template,motif="thin_drop_pendant",sequence=j,thin_band=True))
 return ms

def fire_wall(i,x):
 """Three disjoint party assemblies derived from the actual roof schedule."""
 def profile_wall(name,zone,roof_profile,upstand):
  lower=roof_profile;upper=[(y,z+upstand) for y,z in roof_profile]
  sec=lower+list(reversed(upper));count=len(sec)
  v=[[x-.06,y,z] for y,z in sec]+[[x+.06,y,z] for y,z in sec]
  faces=[list(reversed(range(count))),list(range(count,2*count))]+[[a,(a+1)%count,(a+1)%count+count,a+count] for a in range(count)]
  return mesh(name,v,faces,"sticker_party","party_wall_plaster",carrier_kind="roof_profile_party_fire_wall",seam=i,zone=zone,closed=True,outward_winding=True,starts_above_arcade=True,roof_profile_points=roof_profile,section_points=sec)
 def slope_cap(name,zone,label,a,b,upstand,t=.10):
  ya,za=a;yb,zb=b;x0,x1=x-.07,x+.07;za+=upstand;zb+=upstand
  vv=[[x0,ya,za],[x1,ya,za],[x1,yb,zb],[x0,yb,zb],[x0,ya,za+t],[x1,ya,za+t],[x1,yb,zb+t],[x0,yb,zb+t]]
  ff=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
  return mesh(name,vv,ff,"sticker_party_coping","plaster_trim",carrier_kind="slope_following_party_coping",seam=i,zone=zone,slope=label,closed=True,outward_winding=True,thin_slope_prism=True,x_clearance_m=.01)
 p=f"party_fire_wall_{i}"
 main_profile=[(-D/2,8.25),(-5.9,11.0),(2.2,8.25)];service_profile=[(5.3,6.1),(9.65,7.35),(D/2,6.1)]
 main=profile_wall(p+"_main","main",main_profile,.15);service=profile_wall(p+"_service","service",service_profile,.15)
 airwell=box(p+"_airwell",(x-.06,x+.06,2.2,5.2,0,2.4),"sticker_party","party_wall_plaster",carrier_kind="airwell_vertical_party_wall",seam=i,zone="airwell",open_sky_sides=True)
 airwell_cap=box(p+"_airwell_wall_cap",(x-.07,x+.07,2.2,5.2,2.4,2.5),"sticker_party_cap","plaster_trim",carrier_kind="airwell_party_wall_cap",seam=i,zone="airwell",not_roofing=True)
 copings=[]
 for zone,profile,upstand in (("main",main_profile,.15),("service",service_profile,.15)):
  copings += [slope_cap(f"{p}_{zone}_{label}_slope_coping",zone,label,a,b,upstand) for label,a,b in (("front",profile[0],profile[1]),("rear",profile[1],profile[2]))]
  ry,rz=profile[1];copings.append(box(f"{p}_{zone}_ridge_cap",(x-.07,x+.07,ry-.16,ry+.16,rz+upstand,rz+upstand+.21),"sticker_party_coping","plaster_trim",carrier_kind="party_ridge_cap",seam=i,zone=zone,x_clearance_m=.01,compact=True))
 return [main,airwell,airwell_cap,service],copings,{"main_profile":main_profile,"service_profile":service_profile,"open_sky_y_range_m":[2.2,5.2]}
def build_geometry(size="canonical"):
 if size not in SIZES:raise KeyError(size)
 n,w=SIZES[size];ms=[];aps=[];shops=[];tunnels=[];bals=[];roofs=[];dormers=[];wells=[];service=[]
 for u in range(n):
  x0=-w/2+u*UW;x1=x0+UW;domain=COLORS[u];template=TEMPLATES[u%4]
  # Continuous open tunnel surfaces, columns, and a recessed real shopfront.
  parts=[]
  floor=f"unit_{u}_tunnel_floor";parts.append(floor);ms.append(box(floor,(x0,x1,-D/2,-D/2+TD,0,.12),"sticker_tunnel",domain,carrier_kind="open_tunnel_surface",unit=u))
  # The soffit used to overlap both 0.18m columns, causing systematic Cycles
  # black squares. It is now a central beam between columns plus two explicit
  # outward-owned pale endpoint caps; all solids only meet at boundary planes.
  soffit=f"unit_{u}_tunnel_soffit_beam";parts.append(soffit);ms.append(box(soffit,(x0+.22,x1-.22,-D/2,-D/2+TD,4.05,4.25),"sticker_tunnel_soffit","plaster_trim",carrier_kind="tunnel_soffit_beam",unit=u,trimmed_to_caps=True))
  endpoint_caps=[]
  for side,a,b in (("left",x0+.18,x0+.22),("right",x1-.22,x1-.18)):
   q=f"unit_{u}_soffit_{side}_endpoint_cap";endpoint_caps.append(q);parts.append(q);ms.append(box(q,(a,b,-D/2,-D/2+TD,4.05,4.25),"sticker_pale_trim_endpoint","plaster_trim",carrier_kind="pale_trim_endpoint_cap",unit=u,side=side,outward_terminal_faces=True,cycles_overlap_fix=True))
  sm,shop=shopfront(u,x0,x1,domain,template);ms+=sm;shops.append(shop);tunnels.append({"unit":u,"depth":TD,"parts":parts,"endpoint_caps":endpoint_caps,"street_open":True})
  for side,x in (("left",x0),("right",x1-.18)):ms.append(box(f"unit_{u}_{side}_arcade_column",(x,x+.18,-D/2,-D/2+.30,0,4.25),"sticker_arcade","plaster_trim",carrier_kind="arcade_column",unit=u,trimmed_from_soffit=True))
  # Three independent arch-cut panel bays; no backing wall exists between pane/card.
  cuts=[x0+.12,x0+1.72,x0+3.28,x1-.12]
  for b in range(3):
   am,ap=arch_assembly(u,b,x0+.92+b*1.58,cuts[b],cuts[b+1],domain);ms+=am;aps.append(ap)
  # Template-specific physical identity details.
  ms.append(box(f"unit_{u}_{template}_frieze",(x0+.18,x1-.18,-D/2-.02,-D/2+.10,7.78,8.12),"sticker_frieze",domain,carrier_kind="relief_frieze",unit=u,template=template))
  ms+=template_details(u,x0,x1,template,domain)
  # Main roof terminates at the air-well front edge; service roof begins only
  # after its rear edge, leaving a real open-to-sky volume y=2.2..5.2.
  rm=pitched_roof(u,x0+.08,x1-.08,"main",-D/2,2.2,8.25,11.0);ms.append(rm);roofs.append(rm["name"]);dm=dormer(u,(x0+x1)/2);ms+=dm;dormers.append(f"unit_{u}_louvred_dormer_frame")
  if u in {2,3,4}:
   bm,br=balcony(u,x0,x1,{2:3.8,3:4.2,4:4.0}[u]);ms+=bm;bals.append(br)
  # Rear well is a bounded open-to-sky courtyard with walls, rear opening and service wing/roof.
  ax0,ax1=x0+.65,x1-.65;ay0,ay1=2.2,5.2;wellparts=[]
  for label,b in (("front",(ax0,ax1,ay0,ay0+.16,.1,2.2)),("rear",(ax0,ax1,ay1-.16,ay1,.1,2.2)),("left",(ax0,ax0+.16,ay0+.16,ay1-.16,.1,2.2)),("right",(ax1-.16,ax1,ay0+.16,ay1-.16,.1,2.2))):
   q=f"unit_{u}_airwell_{label}";wellparts.append(q);ms.append(box(q,b,"sticker_airwell",domain,carrier_kind="air_well_wall",unit=u))
  opening=f"unit_{u}_rear_opening";ms.append(box(opening,(ax0+.65,ax1-.65,ay1,ay1+.09,.65,2.0),"sticker_rear_opening","dark_timber",carrier_kind="rear_opening_frame",unit=u));wells.append({"unit":u,"parts":wellparts,"opening":opening,"open_to_sky":True})
  # Main rear enclosure stops around the air-well void; service wing closes the rear.
  rear_left=box(f"unit_{u}_rear_enclosure_left",(x0+.20,ax0,ay0,5.2,0,8.15),"sticker_rear_enclosure",domain,carrier_kind="rear_main_enclosure",unit=u);rear_right=box(f"unit_{u}_rear_enclosure_right",(ax1,x1-.20,ay0,5.2,0,8.15),"sticker_rear_enclosure",domain,carrier_kind="rear_main_enclosure",unit=u)
  # Constrained service wing stops short of its rear elevation. The rear is
  # panelized around two real modest recessed apertures rather than covered by
  # a monolithic wall behind printed windows.
  wing=box(f"unit_{u}_service_wing",(x0+.25,x1-.25,5.3,13.35,0,6.1),"sticker_service",domain,carrier_kind="rear_service_wing",unit=u,completion="constrained",rear_panelized=True)
  wa,wb=(x0+.65,x0+2.15),(x0+2.85,x1-.65);rear_parts=[]
  for label,b in (("sill",(x0+.25,x1-.25,13.35,14.,0,1.15)),("head",(x0+.25,x1-.25,13.35,14.,2.65,6.1)),("left",(x0+.25,wa[0],13.35,14.,1.15,2.65)),("middle",(wa[1],wb[0],13.35,14.,1.15,2.65)),("right",(wb[1],x1-.25,13.35,14.,1.15,2.65))):
   q=f"unit_{u}_service_rear_panel_{label}";rear_parts.append(q);ms.append(box(q,b,"sticker_service_rear",domain,carrier_kind="service_rear_wall_panel",unit=u))
  service_openings=[]
  for j,(a,b) in enumerate((wa,wb)):
   gl=f"unit_{u}_service_rear_window_{j}_glass";card=f"unit_{u}_service_rear_window_{j}_card";frames=[]
   ms.append(mesh(gl,[[a,13.78,1.15],[b,13.78,1.15],[b,13.78,2.65],[a,13.78,2.65]],[[0,1,2,3]],"sticker_service_glass","recessed_glazing",carrier_kind="service_rear_glass",unit=u,opening=j));ms.append(mesh(card,[[a,13.47,1.15],[b,13.47,1.15],[b,13.47,2.65],[a,13.47,2.65]],[[0,1,2,3]],"sticker_service_interior","interior_card",carrier_kind="service_rear_interior_card",unit=u,opening=j))
   for label,bb in (("left",(a-.04,a+.04,13.76,13.84,1.11,2.69)),("right",(b-.04,b+.04,13.76,13.84,1.11,2.69)),("sill",(a+.04,b-.04,13.76,13.84,1.11,1.19)),("head",(a+.04,b-.04,13.76,13.84,2.61,2.69))):
    q=f"unit_{u}_service_rear_window_{j}_{label}";frames.append(q);ms.append(box(q,bb,"sticker_service_frame","dark_timber",carrier_kind="service_rear_window_frame",unit=u,opening=j))
   service_openings.append({"glass":gl,"card":card,"frames":frames})
  sr=pitched_roof(u,x0+.35,x1-.35,"service",5.3,D/2,6.1,7.35);ms += [rear_left,rear_right,wing,sr];service.append({"wing":wing["name"],"roof":sr["name"],"rear_enclosures":[rear_left["name"],rear_right["name"]],"rear_panels":rear_parts,"openings":service_openings,"airwell_y_range_m":[2.2,5.2]})
 # Actual end gable walls close both row ends without blocking the arcade.
 # The old full-depth/full-height terminal overlapped the end arcade column and
 # soffit in Cycles, producing a near-black L. Split it at the tunnel backline:
 # lower wall begins behind the passage; only the upper closure reaches front.
 for end_u,gx0,domain in ((0,-w/2,COLORS[0]),(n-1,w/2-.16,COLORS[n-1])):
  ms.append(box(f"row_end_gable_{end_u}_lower_rear",(gx0,gx0+.16,-D/2+TD,D/2,0,8.25),"sticker_end_gable",domain,carrier_kind="row_end_gable_wall",unit=end_u,starts_behind_arcade=True,terminal_overlap_fix=True))
  ms.append(box(f"row_end_gable_{end_u}_upper_front",(gx0,gx0+.16,-D/2,-D/2+TD,4.25,8.25),"sticker_end_gable_upper",domain,carrier_kind="row_end_gable_upper_closure",unit=end_u,clear_above_arcade=True,terminal_overlap_fix=True))
 # Singleton slope-profile fire walls start behind arcade back line, never blocking tunnel.
 parties=[]
 for i in range(1,n):
  x=-w/2+i*UW;walls,caps,schedule=fire_wall(i,x);ms+=walls;ms+=caps;parties.append({"walls":[wall["name"] for wall in walls],"copings":[c["name"] for c in caps],"seam":i,**schedule})
 g={"archetype_id":ARCHETYPE_ID,"variant_id":VARIANT_ID,"size":size,"reference_evidence":REFS,"dimensions":{"width_m":w,"depth_m":D,"storeys":2},"unit_contract":{"count":n,"width_m":UW,"depth_m":D},"canonical_color_order":COLORS[:n],"physical_templates":[TEMPLATES[i%4] for i in range(n)],"apertures":aps,"shopfronts":shops,"tunnels":tunnels,"balconies":bals,"roofs":roofs,"dormers":dormers,"party_walls":parties,"rear_air_wells":wells,"service_wings":service,"meshes":ms,"hard_stops":["true_arch_cut_panelized_upper_walls","party_walls_start_behind_1_7m_arcade","real_split_shopfronts","closed_thick_roofs_and_slope_firewalls","one_louvred_pitched_cap_dormer_per_unit","bounded_selective_balconies","canonical_color_order_locked","four_physical_facade_templates","bounded_airwells_and_closed_service_roofs","comprehensive_overlap_and_face_ownership_required"]};g["geometry_sha256"]=digest({k:v for k,v in g.items() if k!="geometry_sha256"});return g
if __name__=="__main__":
 for s in SIZES:
  g=build_geometry(s);print(s,len(g["meshes"]),g["geometry_sha256"])
