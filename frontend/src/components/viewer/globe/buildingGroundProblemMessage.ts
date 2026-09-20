export function buildingGroundProblemMessage(reason?: string): string {
  if (reason === 'entrance_connection_required') return 'This raised foundation needs an entrance connection. Open Connections, mark the foot of the steps and choose a street, or move the building to flatter ground.';
  if (reason === 'entrance_anchor_not_at_edge') return 'The entrance anchor does not meet the outer foundation edge. In Connections, place it at the outer foot of the actual entrance steps.';
  if (reason === 'entrance_approach_obstructed') return 'The entrance route is missing or obstructed. Check its street target and keep the approach clear of buildings, plots and vehicle lanes.';
  if (reason === 'entrance_approach_too_short') return 'There is not enough room for this stair approach. Move the building farther from the street, choose another entrance or use flatter ground.';
  if (reason === 'entrance_landing_run_too_short') return 'There is not enough room for the stairs and a level landing at the house. Move the building farther from the street, choose another entrance or use flatter ground.';
  if (reason === 'entrance_terrain_intersection') return 'The proposed entrance steps or landing intersect the measured terrain. Move the building or choose a clearer approach; the ground has not been cut or flattened.';
  if (reason === 'entrance_height_invalid') return 'Set a valid entrance height in Connections and check it against the actual building steps.';
  return reason === 'foundation_exceeds_3m'
    ? 'This building crosses a steep change in ground. Move it to flatter ground or choose a prepared site level.'
    : 'The ground beneath this building could not be confirmed. Wait for the terrain to load, or move it onto measured ground.';
}
