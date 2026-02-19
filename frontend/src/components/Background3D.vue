<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as THREE from 'three';

const props = defineProps<{ isDark: boolean; isReady?: boolean }>();
const containerRef = ref<HTMLDivElement | null>(null);

let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let starGeo: THREE.BufferGeometry;
let stars: THREE.Points;
let material: THREE.PointsMaterial;
let animationId: number;

// === 🎨 配色定義 ===
const COLOR_DARK_BG = 0x1a1a1a;     // 深色模式：深灰底
const COLOR_STAR_DARK = 0xe0cda9;   // 深色模式：淺奶茶色星星

const COLOR_LIGHT_BG = 0xfdfbf7;    // 亮色模式：米白底F
const COLOR_STAR_LIGHT = 0x8d6e63;  // 亮色模式：深咖啡星星

const initThree = () => {
  if (!containerRef.value) return;

  // 1. 場景F
  scene = new THREE.Scene();
  scene.background = new THREE.Color(props.isDark ? COLOR_DARK_BG : COLOR_LIGHT_BG);
  
  // 2. 相機
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
  camera.position.z = 1;
  camera.rotation.x = Math.PI / 2; // 仰望天空的角度

  // 3. 渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  containerRef.value.appendChild(renderer.domElement);

  // 4. 建立星星 (Points)
  // 數量設為 200 顆，保持稀疏感
  const starCount = 200;
  starGeo = new THREE.BufferGeometry();
  
  const positions = new Float32Array(starCount * 3);

  for(let i=0; i<starCount; i++) {
    // 隨機分佈在空間中
    positions[i*3] = (Math.random() - 0.5) * 600;
    positions[i*3+1] = (Math.random() - 0.5) * 600;
    positions[i*3+2] = (Math.random() - 0.5) * 600;
  }

  starGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  
  material = new THREE.PointsMaterial({
    color: props.isDark ? COLOR_STAR_DARK : COLOR_STAR_LIGHT,
    size: 2.5, // 星星大小
    transparent: true,
    opacity: 0.8,
    sizeAttenuation: true // 遠小近大
  });

  stars = new THREE.Points(starGeo, material);
  scene.add(stars);

  window.addEventListener('resize', onWindowResize);
};

// 監聽主題切換
watch(() => props.isDark, (newVal) => {
  if (scene && material) {
    scene.background = new THREE.Color(newVal ? COLOR_DARK_BG : COLOR_LIGHT_BG);
    material.color.setHex(newVal ? COLOR_STAR_DARK : COLOR_STAR_LIGHT);
  }
});

const onWindowResize = () => {
  if (!containerRef.value) return;
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
};

// 動畫迴圈
const animate = () => {
  animationId = requestAnimationFrame(animate);

  if (!props.isReady) return;
  
  if (stars && material) {
    // 1. 極緩慢旋轉 (幾乎靜止，但有一點點生命力)
    stars.rotation.y += 0.0002; 

    // 2. 閃爍效果 (呼吸燈)
    // 利用時間函數產生 0.3 ~ 1.0 之間的透明度變化
    const time = Date.now() * 0.001;
    material.opacity = 0.6 + Math.sin(time) * 0.3;
  }

  renderer.render(scene, camera);
};

onMounted(() => {
  initThree();
  animate();
});

onUnmounted(() => {
  cancelAnimationFrame(animationId);
  window.removeEventListener('resize', onWindowResize);
  if (renderer) renderer.dispose();
});
</script>

<template>
  <div ref="containerRef" class="three-bg"></div>
</template>

<style scoped>
.three-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
}
</style>