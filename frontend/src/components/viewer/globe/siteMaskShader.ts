/** Shared polygon test for mesh fragments and Gaussian centres. */
const MAX_SITE_MASKS = 8;
const MAX_SITE_EDGES = 32;
export const siteMaskFragmentDeclarations = `#define MAX_SITE_MASKS ${MAX_SITE_MASKS}\n#define MAX_SITE_EDGES ${MAX_SITE_EDGES}\nuniform vec4 siteMaskEdges[MAX_SITE_EDGES];\nuniform int siteMaskEdgeCount;\nuniform vec2 siteMaskRanges[MAX_SITE_MASKS];\nuniform int siteMaskCount;\nuniform vec2 siteMaskHeightRange;\nvarying vec3 vSiteMaskLocalPosition;`;
export const siteMaskFragmentTest = `bool insideAnySiteMask = false;
vec2 sitePoint = vSiteMaskLocalPosition.xy;
for (int siteMask = 0; siteMask < MAX_SITE_MASKS; siteMask++) {
  if (siteMask < siteMaskCount) {
    vec2 siteRange = siteMaskRanges[siteMask];
    bool insideCurrentSiteMask = false;
    bool onSiteBoundary = false;
    for (int siteEdge = 0; siteEdge < MAX_SITE_EDGES; siteEdge++) {
      float siteEdgeIndex = float(siteEdge);
      if (siteEdge < siteMaskEdgeCount && siteEdgeIndex >= siteRange.x && siteEdgeIndex < siteRange.x + siteRange.y) {
        vec4 edge = siteMaskEdges[siteEdge];
        vec2 a = edge.xy;
        vec2 b = edge.zw;
        vec2 direction = b - a;
        float edgeCross = direction.x * (sitePoint.y - a.y) - direction.y * (sitePoint.x - a.x);
        if (abs(edgeCross) <= 0.000001 * max(1.0, length(direction))
            && all(greaterThanEqual(sitePoint, min(a, b) - vec2(0.000001)))
            && all(lessThanEqual(sitePoint, max(a, b) + vec2(0.000001)))) onSiteBoundary = true;
        // Horizontal edges never divide by zero. The half-open crossing rule
        // counts shared vertices once and preserves re-entrant corners.
        if ((a.y > sitePoint.y) != (b.y > sitePoint.y)) {
          float crossingX = direction.x * (sitePoint.y - a.y) / direction.y + a.x;
          if (sitePoint.x < crossingX) insideCurrentSiteMask = !insideCurrentSiteMask;
        }
      }
    }
    if (insideCurrentSiteMask || onSiteBoundary) insideAnySiteMask = true;
  }
}
if (insideAnySiteMask && vSiteMaskLocalPosition.z >= siteMaskHeightRange.x && vSiteMaskLocalPosition.z <= siteMaskHeightRange.y) discard;`;
