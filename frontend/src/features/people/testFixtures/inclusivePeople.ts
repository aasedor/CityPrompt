// Controlled catalogue data lets runtime regressions run before asset promotion.
const base = { category: 'People', kind: 'object', dimensions: [1, 1, 1.7], color: '#667788', datumLift: 0 };
export const inclusivePeople = [
  { ...base, id: 'people-inclusive-manual-wheelchair', label: 'Manual wheelchair user', description: 'Adult using a manual wheelchair.', url: '/test/manual-wheelchair.glb',
    peopleRepresentation: { defaultAction: 'sitting', supportedActions: ['sitting'], personCount: 1, description: 'Adult using a manual wheelchair', fixedPose: true } },
  { ...base, id: 'people-inclusive-family-parent-child', label: 'Parent and child', description: 'Parent and child together.', url: '/test/parent-child.glb',
    peopleRepresentation: { defaultAction: 'standing', supportedActions: ['standing'], personCount: 2, description: 'Parent and child together', fixedPose: true } },
  { ...base, id: 'people-inclusive-family-stroller', label: 'Parent with stroller', description: 'Parent and infant in a stroller.', url: '/test/stroller.glb',
    peopleRepresentation: { defaultAction: 'standing', supportedActions: ['standing'], personCount: 2, description: 'Adult and infant in a stroller, with the adult standing', fixedPose: true } },
];
