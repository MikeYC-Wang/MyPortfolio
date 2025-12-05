<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import html2canvas from 'html2canvas';

gsap.registerPlugin(ScrollTrigger);

const props = defineProps<{ isDark: boolean }>();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);

// Three.js 變數
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;
let animationId: number;

// === ☁️ 漂浮背景變數 ===
let floatingElements: { sprite: THREE.Sprite; velocity: THREE.Vector3 }[] = [];

// === 🔍 滾輪縮放控制變數 ===
let extraZoomDistance = 0;
const MAX_EXTRA_ZOOM = 10;
const BASE_CAMERA_Z = 6;

// === 🌐 粒子地球變數 ===
let earthMesh: THREE.Points | null = null;
const earthRadius = 0.5;

// 定義要顯示的程式語言
const languages = [
  { name: 'HTML5', color: '#E34F26', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg' },
  { name: 'CSS3', color: '#1572B6', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg' },
  { name: 'JavaScript', color: '#F7DF1E', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg' },
  { name: 'TypeScript', color: '#3178C6', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg' },
  { name: 'Vue.js', color: '#4FC08D', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vuejs/vuejs-original.svg' },
  { name: 'Python', color: '#3776AB', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg' },
  { name: 'Node.js', color: '#339933', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg' },
  { name: 'React', color: '#61DAFB', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg' },
  { name: 'Git', color: '#F05032', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg' },
  { name: 'Docker', color: '#2496ED', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg' },
  { name: 'C#', color: '#178600', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/csharp/csharp-original.svg' },
  { name: 'Angular', color: '#DD0031', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg' },
  { name: 'Sass', color: '#CC6699', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sass/sass-original.svg' },
];

// 輔助函式：繪製標籤貼圖
const createLabelTexture = (text: string, color: string, iconUrl: string): Promise<THREE.CanvasTexture> => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const size = 256; 
    canvas.width = size;
    canvas.height = size;

    if (!ctx) return;

    const img = new Image();
    img.crossOrigin = "Anonymous"; 
    img.src = iconUrl;

    img.onload = () => {
      const iconSize = size * 0.5;
      ctx.drawImage(img, (size - iconSize) / 2, size * 0.1, iconSize, iconSize);
      ctx.font = `bold ${size * 0.15}px Arial, sans-serif`;
      ctx.fillStyle = color;
      ctx.textAlign = 'center';
      ctx.shadowColor = color;
      ctx.shadowBlur = 10;
      ctx.fillText(text, size / 2, size * 0.85);
      const texture = new THREE.CanvasTexture(canvas);
      texture.needsUpdate = true;
      resolve(texture);
    };
    img.onerror = () => {
      ctx.font = `bold ${size * 0.15}px Arial, sans-serif`;
      ctx.fillStyle = color;
      ctx.textAlign = 'center';
      ctx.fillText(text, size / 2, size * 0.5);
      resolve(new THREE.CanvasTexture(canvas));
    }
  });
};

// 建立漂浮背景
const initFloatingBackground = async () => {
  const elementsToCreate = [...languages, ...languages];
  for (const lang of elementsToCreate) {
    const texture = await createLabelTexture(lang.name, lang.color, lang.icon);
    const material = new THREE.SpriteMaterial({ 
      map: texture, 
      transparent: true,
      opacity: 0.7, 
      depthWrite: false 
    });
    const sprite = new THREE.Sprite(material);
    sprite.position.set(
      (Math.random() - 0.5) * 25, 
      (Math.random() - 0.5) * 15, 
      -5 - Math.random() * 20
    );
    const scale = 1 + Math.random();
    sprite.scale.set(scale, scale, 1);
    const velocity = new THREE.Vector3(
      (Math.random() - 0.5) * 0.01,
      (Math.random() - 0.5) * 0.01,
      0
    );
    scene.add(sprite);
    floatingElements.push({ sprite, velocity });
  }
};

// 建立粒子地球
const createParticleEarth = () => {
    const particles = 20000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particles * 3);
    
    for (let i = 0; i < particles; i++) {
        const phi = Math.acos(1 - 2 * Math.random());
        const theta = 2 * Math.PI * Math.random();

        positions[i * 3] = earthRadius * Math.sin(phi) * Math.cos(theta);
        positions[i * 3 + 1] = earthRadius * Math.sin(phi) * Math.sin(theta);
        positions[i * 3 + 2] = earthRadius * Math.cos(phi);
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
        color: 0x00ffff,
        size: 0.01,
        blending: THREE.AdditiveBlending,
        transparent: true,
        sizeAttenuation: true
    });

    earthMesh = new THREE.Points(geometry, material);
    earthMesh.position.set(-4, -1.5, -2); 
    
    scene.add(earthMesh);
};

// === 🖥️ 初始化 3D 場景 ===
const initScene = async () => {
  if (!canvasRef.value || !containerRef.value) return;

  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(props.isDark ? 0x000000 : 0xffffff, 0.03);
  scene.background = null; 

  camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 1.5, BASE_CAMERA_Z); 
  
  renderer = new THREE.WebGLRenderer({ 
    canvas: canvasRef.value, 
    alpha: true, 
    antialias: true 
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;

  // 控制器設定
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.enableZoom = false; 
  controls.enablePan = false;
  controls.mouseButtons = {
    LEFT: null as any,
    MIDDLE: null as any,
    RIGHT: THREE.MOUSE.ROTATE
  };

  const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
  scene.add(ambientLight);
  
  const dirLight = new THREE.DirectionalLight(0xffffff, 2);
  dirLight.position.set(5, 10, 7);
  dirLight.castShadow = true;
  scene.add(dirLight);

  const fillLight = new THREE.PointLight(0x4455ff, 1);
  fillLight.position.set(-5, 2, 3);
  scene.add(fillLight);

  // 初始化漂浮背景與粒子地球
  await initFloatingBackground();
  createParticleEarth(); 

  // 載入模型
  const loader = new GLTFLoader();
  loader.load(
    '/models/Fullsetup.glb', 
    (gltf) => {
      const model = gltf.scene;
      
      const box = new THREE.Box3().setFromObject(model);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());

      const targetWidth = 4; 
      const scale = targetWidth / size.x;
      
      model.scale.set(scale, scale, scale);

      model.position.x = -center.x * scale;
      model.position.y = -center.y * scale - 0.5;
      model.position.z = -center.z * scale;

      model.rotation.y = 0; 

      scene.add(model);
      
      setupScrollAnimation(); 
    },
    undefined,
    (error) => console.error('模型載入失敗:', error)
  );
};

// === 🖱️ 滾輪縮放邏輯 ===
const handleWheel = (event: WheelEvent) => {
  if (window.scrollY === 0) {
    const zoomSpeed = 0.01;
    let newExtra = extraZoomDistance - event.deltaY * zoomSpeed;
    newExtra = Math.max(0, Math.min(newExtra, MAX_EXTRA_ZOOM));

    if (newExtra !== extraZoomDistance || (extraZoomDistance > 0 && event.deltaY > 0)) {
      event.preventDefault();
      extraZoomDistance = newExtra;
      updateCameraDistance();
    }
  } else {
    extraZoomDistance = 0;
  }
};

const updateCameraDistance = () => {
  if (!camera || !controls) return;
  const direction = new THREE.Vector3().subVectors(camera.position, controls.target).normalize();
  const targetDistance = BASE_CAMERA_Z + extraZoomDistance;
  camera.position.copy(direction.multiplyScalar(targetDistance).add(controls.target));
};

// GSAP 動畫
const setupScrollAnimation = () => {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: containerRef.value,
      start: "top top",
      end: "+=1500",
      scrub: 1,
      pin: true,
    }
  });

  tl
  .to(camera.position, { x: 0, y: 0.8, z: 0.8, duration: 5, ease: "power2.inOut" })
  .to(camera.position, { z: -2, duration: 1, ease: "none" })
  .to(canvasRef.value, { opacity: 0, duration: 0.5 }, "<0.5");
};

const animate = () => {
  animationId = requestAnimationFrame(animate);
  if (controls) controls.update();

  // 更新漂浮背景位置
  floatingElements.forEach(el => {
    el.sprite.position.add(el.velocity);
    const limit = 15;
    if (el.sprite.position.x > limit) el.sprite.position.x = -limit;
    if (el.sprite.position.x < -limit) el.sprite.position.x = limit;
    if (el.sprite.position.y > 10) el.sprite.position.y = -10;
    if (el.sprite.position.y < -10) el.sprite.position.y = 10;
  });

  // 🌐 粒子地球自轉
  if (earthMesh) {
    earthMesh.rotation.y += 0.001; 
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
};

const handleResize = () => {
  if (camera && renderer) {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }
};

// === 核心修正：加入類型檢查以安全清理資源 ===
const safeDisposeMaterial = (material: THREE.Material | THREE.Material[]) => {
  if (Array.isArray(material)) {
    material.forEach(m => m.dispose());
  } else {
    material.dispose();
  }
};

onMounted(async () => {
  await initScene();
  animate();
  window.addEventListener('resize', handleResize);
  window.addEventListener('wheel', handleWheel, { passive: false });
});

onUnmounted(() => {
  cancelAnimationFrame(animationId);
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('wheel', handleWheel);
  ScrollTrigger.getAll().forEach(t => t.kill());
  if (renderer) renderer.dispose();
  if (controls) controls.dispose();
  
  // 清理漂浮元素資源 (已修復類型錯誤)
  floatingElements.forEach(el => {
    const material = el.sprite.material;
    
    // 1. 清理貼圖 (Texture)
    // 必須檢查 material 是否為陣列，因為陣列上沒有 .map 屬性
    if (!Array.isArray(material) && material.map) {
      material.map.dispose();
    }
    
    // 2. 清理材質本身 (使用安全函式)
    safeDisposeMaterial(material);
  });
  
  // 清理粒子地球資源 (已修復類型錯誤)
  if (earthMesh) {
    earthMesh.geometry.dispose();
    safeDisposeMaterial(earthMesh.material);
  }
});
</script>

<template>
  <div ref="containerRef" class="intro-container">
    <canvas ref="canvasRef" class="webgl-canvas"></canvas>
    
    <div class="scroll-hint">
      <p>Scroll Up to Zoom Out / Right Click to Rotate</p>
      <p>Scroll Down to Enter</p>
      <div class="arrow">⬇</div>
    </div>
  </div>
</template>

<style scoped>
/* 樣式完全保留 */
.intro-container {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background: transparent;
  pointer-events: auto; 
}

.webgl-canvas {
  width: 100%;
  height: 100%;
  display: block;
  outline: none;
}

.scroll-hint {
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  color: var(--text-color);
  text-align: center;
  font-weight: bold;
  opacity: 0.8;
  animation: bounce 2s infinite;
  pointer-events: none;
  z-index: 5;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
  width: 100%;
}

.arrow { font-size: 1.5rem; margin-top: 0.5rem; }

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {transform: translateX(-50%) translateY(0);}
  40% {transform: translateX(-50%) translateY(-10px);}
  60% {transform: translateX(-50%) translateY(-5px);}
}
</style>