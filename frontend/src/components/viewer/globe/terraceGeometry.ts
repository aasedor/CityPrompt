import * as THREE from 'three';

type Vertex = [number, number, number];
export type Cutout = Array<[number, number]>;

/** Subtract convex footprints from triangles. Sequential subtraction handles
 * touching/overlapping pad and ramp openings without overlapping Shape holes.
 * Interpolate Z while clipping so this also opens vertical retaining faces. */
export function cutGeometry(source: THREE.BufferGeometry, cutouts: Cutout[]): THREE.BufferGeometry {
  const attr = source.getAttribute('position'), index = source.getIndex(), output: number[] = [];
  const count = index?.count ?? attr.count;
  for (let i=0;i<count;i+=3) {
    let pieces: Vertex[][] = [[0,1,2].map(k=>{const n=index?index.getX(i+k):i+k;return [attr.getX(n),attr.getY(n),attr.getZ(n)] as Vertex;})];
    for (const raw of cutouts) {
      if(raw.length<3)continue;
      const signed = raw.reduce((sum,a,j)=>{const b=raw[(j+1)%raw.length];return sum+a[0]*b[1]-b[0]*a[1];},0);
      const ring=signed<0?[...raw].reverse():raw;
      const outside: Vertex[][]=[];
      for(const piece of pieces) {
        let remaining=piece;
        for(let j=0;j<ring.length&&remaining.length>=3;j++) {
          const a=ring[j],b=ring[(j+1)%ring.length];
          const distance=(v:Vertex)=>(b[0]-a[0])*(v[1]-a[1])-(b[1]-a[1])*(v[0]-a[0]);
          const clip=(inside:boolean)=>{
            const result:Vertex[]=[];
            for(let n=0;n<remaining.length;n++) {
              const p=remaining[n],q=remaining[(n+1)%remaining.length],dp=distance(p),dq=distance(q);
              const pin=inside?dp>=-1e-8:dp< -1e-8,qin=inside?dq>=-1e-8:dq< -1e-8;
              if(pin)result.push(p);
              if(pin!==qin&&Math.abs(dp-dq)>1e-12) {const t=dp/(dp-dq);result.push(p.map((v,k)=>v+t*(q[k]-v)) as Vertex);}
            }
            return result;
          };
          const out=clip(false),within=clip(true);
          if(out.length>=3)outside.push(out);
          remaining=within;
        }
      }
      pieces=outside;
    }
    for(const piece of pieces)for(let j=1;j<piece.length-1;j++)output.push(...piece[0],...piece[j],...piece[j+1]);
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(output,3));
  geometry.computeVertexNormals();geometry.computeBoundingSphere();
  return geometry;
}

export function stripFootprint(a: [number,number], b: [number,number], width: number): Cutout {
  const dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy)||1,nx=-dy/length*width/2,ny=dx/length*width/2;
  return [[a[0]-nx,a[1]-ny],[b[0]-nx,b[1]-ny],[b[0]+nx,b[1]+ny],[a[0]+nx,a[1]+ny]];
}
