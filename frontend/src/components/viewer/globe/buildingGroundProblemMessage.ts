export function buildingGroundProblemMessage(reason?: string): string {
  return reason === 'foundation_exceeds_3m'
    ? 'This building crosses a steep change in ground. Move it to flatter ground or choose a prepared site level.'
    : 'The ground beneath this building could not be confirmed. Wait for the terrain to load, or move it onto measured ground.';
}
