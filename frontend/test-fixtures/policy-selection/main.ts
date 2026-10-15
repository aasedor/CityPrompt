import * as THREE from 'three';
import { pickEditableZoneBeforePolicy } from '../../src/features/policyPlans/policyPicking';
import { direct3DInstanceUserData, direct3DZoneInstanceDescriptor } from '../../src/components/viewer/globe/direct3dCapture';

// Local-only browser regression: the production picker, with deterministic
// geometry and a prepared boundary/reference layer above the model footprints.
const scene = new THREE.Scene();
scene.background = new THREE.Color('#fff9ed');
const camera = new THREE.PerspectiveCamera(45, 1.5, .1, 200);
camera.up.set(0, 0, 1);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(900, 600);
document.querySelector('main')!.append(renderer.domElement);
const ray = new THREE.Raycaster();
const zones = [
  { id: 'site', zone_type: 'site_boundary' },
  { id: 'Building', zone_type: 'building' },
  { id: 'Park', zone_type: 'green_space' },
  { id: 'Street', zone_type: 'road' },
];
for (const [id, role, x, width, height, color] of [
  ['Building', 'building', -12, 9, 8, '#9bbeca'],
  ['Park', 'park', 0, 8, 1, '#8eae53'],
  ['Street', 'street', 12, 7, .5, '#666666'],
] as const) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, 12, height), new THREE.MeshBasicMaterial({ color }));
  mesh.position.set(x, 0, height / 2);
  mesh.userData = direct3DInstanceUserData(direct3DZoneInstanceDescriptor(id, role));
  scene.add(mesh);
}
const boundary = new THREE.Mesh(new THREE.PlaneGeometry(48, 30), new THREE.MeshBasicMaterial({ color: '#c7e58e', transparent: true, opacity: .25, side: THREE.DoubleSide }));
boundary.position.z = 10;
boundary.userData = direct3DInstanceUserData(direct3DZoneInstanceDescriptor('site', 'ground'));
scene.add(boundary);
function render(top: boolean) {
  camera.position.set(0, top ? -.001 : -40, top ? 60 : 40);
  camera.lookAt(0, 0, 0);
  camera.updateMatrixWorld(true);
  scene.updateMatrixWorld(true);
  renderer.render(scene, camera);
}
document.querySelector('#angle')!.addEventListener('click', () => render(false));
document.querySelector('#top')!.addEventListener('click', () => render(true));
renderer.domElement.addEventListener('click', event => {
  const rect = renderer.domElement.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2((event.clientX - rect.left) / rect.width * 2 - 1, 1 - (event.clientY - rect.top) / rect.height * 2), camera);
  const selected = pickEditableZoneBeforePolicy(scene, ray, zones);
  document.querySelector('#selection')!.textContent = selected ? `Selected: ${selected}` : 'Selected: zoning';
}, true);
render(false);
