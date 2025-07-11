const THREE = require('three');

let scene, camera, renderer, mesh, is3D;

function initAvatar(canvasId, enable3D) {
  const canvas = document.getElementById(canvasId);
  is3D = enable3D;
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);

  let geometry, material;
  if (is3D) {
    geometry = new THREE.SphereGeometry(1, 32, 32);  // Placeholder for mesh from InstantMesh
    material = new THREE.MeshPhongMaterial({ color: 0x00bfff });
  } else {
    const texture = new THREE.TextureLoader().load('assets/avatar.jpg');
    geometry = new THREE.PlaneGeometry(4, 5);
    material = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide });
  }
  mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
  const light = new THREE.DirectionalLight(0xffffff);
  light.position.set(0, 0, 5);
  scene.add(light);
  camera.position.z = 5;

  animate();
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

function updateMorph(viseme) {
  if (mesh) {
    // Simple animation based on viseme (e.g., scale mouth)
    mesh.scale.y = viseme.code === 'A' ? 1.1 : 1.0;  // Example
  }
}

// Export for use in ui.js
module.exports = { initAvatar, updateMorph };