const resolution = 720;

const scene1 = new THREE.Scene();
const scene2 = new THREE.Scene();
const aspect = window.innerWidth / 2 / window.innerHeight;
const camera1 = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
const camera2 = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
const renderer1 = new THREE.WebGLRenderer({
  canvas: document.getElementById("canvas1"),
});
const renderer2 = new THREE.WebGLRenderer({
  canvas: document.getElementById("canvas2"),
});
renderer1.setSize(window.innerWidth / 2, window.innerHeight);
renderer2.setSize(window.innerWidth / 2, window.innerHeight);

camera1.position.z = 8;
camera2.position.z = 8;
const interocularDistance = 0.1;
camera1.position.x -= interocularDistance / 2;
camera2.position.x += interocularDistance / 2;

const textureLoader = new THREE.TextureLoader();
let originalImage, depthMap;
let isInitialized = false;

textureLoader.load("Azrael2.jpg", function (texture) {
  originalImage = texture;
  init();
});
textureLoader.load("Azrael2DepthMap.jpg", function (texture) {
  depthMap = texture;
  init();
});

function init() {
  if (originalImage && depthMap && !isInitialized) {
    isInitialized = true;
    setSolidMode();
  }
}

const geometry = new THREE.PlaneGeometry(5, 5, resolution, resolution);
let plane1, plane2;
let displacementScale = 1;

let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };

const controlsContainer1 = document.getElementById("controlsContainer1");
const controlsContainer2 = document.getElementById("controlsContainer2");

const onMouseDown = (event) => {
  isDragging = true;
  controlsContainer1.classList.add("hidden");
  controlsContainer2.classList.add("hidden");
};
const onMouseUp = (event) => {
  isDragging = false;
  controlsContainer1.classList.remove("hidden");
  controlsContainer2.classList.remove("hidden");
};
const onMouseMove = (event) => {
  if (isDragging) {
    const deltaMove = {
      x: event.clientX - previousMousePosition.x,
      y: event.clientY - previousMousePosition.y,
    };

    const deltaRotationQuaternion = new THREE.Quaternion().setFromEuler(
      new THREE.Euler(deltaMove.y * 0.01, deltaMove.x * 0.01, 0, "XYZ")
    );

    plane1.quaternion.multiplyQuaternions(
      deltaRotationQuaternion,
      plane1.quaternion
    );
    plane2.quaternion.multiplyQuaternions(
      deltaRotationQuaternion,
      plane2.quaternion
    );

    previousMousePosition = { x: event.clientX, y: event.clientY };
  } else {
    previousMousePosition = { x: event.clientX, y: event.clientY };
  }
  renderer1.render(scene1, camera1);
  renderer2.render(scene2, camera2);
};

renderer1.domElement.addEventListener("mousedown", onMouseDown);
renderer1.domElement.addEventListener("mouseup", onMouseUp);
renderer1.domElement.addEventListener("mousemove", onMouseMove);

renderer2.domElement.addEventListener("mousedown", onMouseDown);
renderer2.domElement.addEventListener("mouseup", onMouseUp);
renderer2.domElement.addEventListener("mousemove", onMouseMove);

const onWheel = (event) => {
  event.preventDefault();
  const delta = event.deltaY * 0.01;
  camera1.position.z = Math.max(1, Math.min(10, camera1.position.z + delta));
  camera2.position.z = Math.max(1, Math.min(10, camera2.position.z + delta));
  renderer1.render(scene1, camera1);
  renderer2.render(scene2, camera2);
};

renderer1.domElement.addEventListener("wheel", onWheel);
renderer2.domElement.addEventListener("wheel", onWheel);

function setSolidMode() {
  const solidMaterial = new THREE.ShaderMaterial({
    uniforms: {
      texture1: { type: "t", value: originalImage },
      displacementMap: { type: "t", value: depthMap },
      displacementScale: { value: displacementScale },
    },
    vertexShader: `
            uniform sampler2D displacementMap;
            uniform float displacementScale;
            varying vec2 vUv;
            void main() {
                vUv = uv;
                vec3 newPosition = position + normal * texture2D(displacementMap, uv).r * displacementScale;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
            }
        `,
    fragmentShader: `
            uniform sampler2D texture1;
            varying vec2 vUv;
            void main() {
                gl_FragColor = texture2D(texture1, vUv);
            }
        `,
    side: THREE.DoubleSide,
  });

  scene1.remove(plane1);
  scene2.remove(plane2);
  plane1 = new THREE.Mesh(geometry, solidMaterial);
  plane2 = new THREE.Mesh(geometry, solidMaterial);
  scene1.add(plane1);
  scene2.add(plane2);
  setActiveButton("solidButton1", "solidButton2");
  renderer1.render(scene1, camera1);
  renderer2.render(scene2, camera2);
}

function setPointCloudMode() {
  const vertices = [];
  const colors = [];

  const canvas = document.createElement("canvas");
  canvas.width = resolution;
  canvas.height = resolution;
  const context = canvas.getContext("2d");
  context.drawImage(originalImage.image, 0, 0, resolution, resolution);
  const imageData = context.getImageData(0, 0, resolution, resolution).data;

  context.drawImage(depthMap.image, 0, 0, resolution, resolution);
  const depthData = context.getImageData(0, 0, resolution, resolution).data;

  for (let y = 0; y < resolution; y++) {
    for (let x = 0; x < resolution; x++) {
      const i = (y * resolution + x) * 4;
      const r = imageData[i] / 255;
      const g = imageData[i + 1] / 255;
      const b = imageData[i + 2] / 255;
      const z = (depthData[i] / 255) * displacementScale;

      vertices.push(
        (x / resolution) * 5 - 2.5,
        (1 - y / resolution) * 5 - 2.5,
        z
      );
      colors.push(r, g, b);
    }
  }

  const pointGeometry = new THREE.BufferGeometry();
  pointGeometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(vertices, 3)
  );
  pointGeometry.setAttribute(
    "color",
    new THREE.Float32BufferAttribute(colors, 3)
  );

  const pointsMaterial = new THREE.PointsMaterial({
    size: 0.02,
    vertexColors: true,
  });
  const points1 = new THREE.Points(pointGeometry, pointsMaterial);
  const points2 = new THREE.Points(pointGeometry, pointsMaterial);

  scene1.remove(plane1);
  scene2.remove(plane2);
  plane1 = points1;
  plane2 = points2;
  scene1.add(plane1);
  scene2.add(plane2);
  setActiveButton("pointCloudButton1", "pointCloudButton2");
  renderer1.render(scene1, camera1);
  renderer2.render(scene2, camera2);
}

function setWireframeMode() {
  const vertices = [];
  const indices = [];
  const colors = [];

  const canvas = document.createElement("canvas");
  canvas.width = resolution;
  canvas.height = resolution;
  const context = canvas.getContext("2d");
  context.drawImage(originalImage.image, 0, 0, resolution, resolution);
  const imageData = context.getImageData(0, 0, resolution, resolution).data;

  context.drawImage(depthMap.image, 0, 0, resolution, resolution);
  const depthData = context.getImageData(0, 0, resolution, resolution).data;

  for (let y = 0; y < resolution; y++) {
    for (let x = 0; x < resolution; x++) {
      const i = (y * resolution + x) * 4;
      const r = imageData[i] / 255;
      const g = imageData[i + 1] / 255;
      const b = imageData[i + 2] / 255;
      const z = (depthData[i] / 255) * displacementScale;

      const vx = (x / resolution) * 5 - 2.5;
      const vy = (1 - y / resolution) * 5 - 2.5;
      vertices.push(vx, vy, z);
      colors.push(r, g, b);

      if (x < resolution - 1 && y < resolution - 1) {
        const a = x + y * resolution;
        const b = x + 1 + y * resolution;
        const c = x + (y + 1) * resolution;
        const d = x + 1 + (y + 1) * resolution;

        indices.push(a, b);
        indices.push(a, c);
        indices.push(b, d);
        indices.push(c, d);

        indices.push(a, d);
        indices.push(b, c);
      }
    }
  }

  const wireframeGeometry = new THREE.BufferGeometry();
  wireframeGeometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(vertices, 3)
  );
  wireframeGeometry.setAttribute(
    "color",
    new THREE.Float32BufferAttribute(colors, 3)
  );
  wireframeGeometry.setIndex(indices);

  const wireframeMaterial = new THREE.LineBasicMaterial({ vertexColors: true });
  const wireframe1 = new THREE.LineSegments(
    wireframeGeometry,
    wireframeMaterial
  );
  const wireframe2 = new THREE.LineSegments(
    wireframeGeometry,
    wireframeMaterial
  );

  scene1.remove(plane1);
  scene2.remove(plane2);
  plane1 = wireframe1;
  plane2 = wireframe2;
  scene1.add(plane1);
  scene2.add(plane2);
  setActiveButton("wireframeButton1", "wireframeButton2");
  renderer1.render(scene1, camera1);
  renderer2.render(scene2, camera2);
}

function setActiveButton(activeButtonId1, activeButtonId2) {
  const buttons1 = document.querySelectorAll(`#controlsContainer1 button`);
  buttons1.forEach((button) => {
    if (button.id === activeButtonId1) {
      button.classList.add("active-button");
    } else {
      button.classList.remove("active-button");
    }
  });

  const buttons2 = document.querySelectorAll(`#controlsContainer2 button`);
  buttons2.forEach((button) => {
    if (button.id === activeButtonId2) {
      button.classList.add("active-button");
    } else {
      button.classList.remove("active-button");
    }
  });
}

document.getElementById("solidButton1").addEventListener("click", setSolidMode);
document.getElementById("solidButton2").addEventListener("click", setSolidMode);

document
  .getElementById("pointCloudButton1")
  .addEventListener("click", setPointCloudMode);
document
  .getElementById("pointCloudButton2")
  .addEventListener("click", setPointCloudMode);

document
  .getElementById("wireframeButton1")
  .addEventListener("click", setWireframeMode);
document
  .getElementById("wireframeButton2")
  .addEventListener("click", setWireframeMode);

document.getElementById("depthSlider1").addEventListener("input", (event) => {
  displacementScale = event.target.value;
  document.getElementById("depthSlider2").value = displacementScale;
  updateDepth();
});
document.getElementById("depthSlider2").addEventListener("input", (event) => {
  displacementScale = event.target.value;
  document.getElementById("depthSlider1").value = displacementScale;
  updateDepth();
});

function updateDepth() {
  switch (document.querySelector(".active-button").id) {
    case "solidButton1":
    case "solidButton2":
      setSolidMode();
      break;
    case "pointCloudButton1":
    case "pointCloudButton2":
      setPointCloudMode();
      break;
    case "wireframeButton1":
    case "wireframeButton2":
      setWireframeMode();
      break;
  }
}

window.addEventListener("resize", () => {
  const aspect = window.innerWidth / 2 / window.innerHeight;
  camera1.aspect = aspect;
  camera1.updateProjectionMatrix();
  camera2.aspect = aspect;
  camera2.updateProjectionMatrix();
  renderer1.setSize(window.innerWidth / 2, window.innerHeight);
  renderer2.setSize(window.innerWidth / 2, window.innerHeight);
  renderer1.render(scene1, camera1);
  renderer2.render(scene2, camera2);
});
