<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import VscodeScreen from './VscodeScreen.vue';

gsap.registerPlugin(ScrollTrigger);

// 定義事件
const emit = defineEmits(['enter-site']);

const props = defineProps<{ isDark: boolean }>();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);
const vscodeScreenRef = ref<InstanceType<typeof VscodeScreen> & { turnOn: () => Promise<void>, isPoweredOn: boolean } | null>(null);

// 主要場景變數
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;

// HUD 場景變數
let hudScene: THREE.Scene;
let hudCamera: THREE.OrthographicCamera;

let animationId: number;
let screenTexture: THREE.CanvasTexture | null = null;
let floatingElements: { sprite: THREE.Sprite; velocity: THREE.Vector3 }[] = [];
let earthMesh: THREE.Points | null = null;
let extraZoomDistance = 0;
const MAX_EXTRA_ZOOM = 10;
const BASE_CAMERA_Z = 6;

// 互動與模型變數
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let pcCaseObject: THREE.Object3D | null = null; 
let monitorMesh: THREE.Mesh | null = null; 
let startHintSprite: THREE.Sprite | null = null; 
let isHoveringPc = false;

// 程式語言圖示
const languages = [
  { name: 'HTML5', color: '#E34F26', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg' },
  { name: 'CSS3', color: '#1572B6', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg' },
  { name: 'JavaScript', color: '#F7DF1E', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg' },
  { name: 'TypeScript', color: '#3178C6', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg' },
  { name: 'Vue.js', color: '#4FC08D', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vuejs/vuejs-original.svg' },
  { name: 'Python', color: '#3776AB', icon: '/python-logo.png' },
  { name: 'Node.js', color: '#339933', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg' },
  { name: 'React', color: '#61DAFB', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg' },
  { name: 'Git', color: '#F05032', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg' },
  { name: 'Docker', color: '#2496ED', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg' },
  { name: 'C#', color: '#178600', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/csharp/csharp-original.svg' },
  { name: 'Angular', color: '#DD0031', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg' },
  { name: 'Sass', color: '#CC6699', icon: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sass/sass-original.svg' },
];

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

const createHintTexture = (text: string): THREE.CanvasTexture => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const width = 512;
    const height = 128;
    canvas.width = width;
    canvas.height = height;

    if (ctx) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'; 
        ctx.beginPath();
        ctx.roundRect(10, 10, width - 20, height - 20, 30);
        ctx.fill();
        
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 6;
        ctx.stroke();

        ctx.font = 'bold 50px "Microsoft JhengHei", Arial, sans-serif';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = '#00ffff';
        ctx.shadowBlur = 10;
        ctx.fillText(text, width / 2, height / 2);
    }
    
    return new THREE.CanvasTexture(canvas);
};

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
    sprite.position.set((Math.random() - 0.5) * 25, (Math.random() - 0.5) * 15, -5 - Math.random() * 20);
    const scale = 1 + Math.random();
    sprite.scale.set(scale, scale, 1);
    const velocity = new THREE.Vector3((Math.random() - 0.5) * 0.01, (Math.random() - 0.5) * 0.01, 0);
    scene.add(sprite);
    floatingElements.push({ sprite, velocity });
  }
};

const createTexturedEarth = async () => {
    const mapUrl = 'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_specular_2048.jpg';
    const img = new Image();
    img.crossOrigin = "Anonymous";
    
    return new Promise<void>((resolve, reject) => {
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (!ctx) { reject(); return; }
            
            const width = img.width;
            const height = img.height;
            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0);
            
            const imgData = ctx.getImageData(0, 0, width, height);
            const data = imgData.data;
            
            const positions: number[] = [];
            const colors: number[] = [];
            const particleCount = 70000; 
            const radius = 1; 

            for (let i = 0; i < particleCount; i++) {
                const u = Math.random();
                const v = Math.random();
                const x = Math.floor(u * width);
                const y = Math.floor(v * height);
                const index = (y * width + x) * 4; 
                
                const brightness = data[index] || 0;
                const isLand = brightness > 50;

                if (isLand || Math.random() < 0.15) {
                    const phi = v * Math.PI; 
                    const theta = u * Math.PI * 2; 
                    const px = -radius * Math.sin(phi) * Math.cos(theta);
                    const py = radius * Math.cos(phi);
                    const pz = radius * Math.sin(phi) * Math.sin(theta);
                    positions.push(px, py, pz);

                    const color = new THREE.Color();
                    if (isLand) color.setHex(0x44aaff); 
                    else color.setHex(0xffffff); 
                    colors.push(color.r, color.g, color.b);
                }
            }
            
            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
            
            const material = new THREE.PointsMaterial({
                vertexColors: true,
                size: 0.008,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending,
            });
            
            earthMesh = new THREE.Points(geometry, material);
            earthMesh.scale.set(0.18, 0.18, 0.18);
            
            const aspect = window.innerWidth / window.innerHeight;
            earthMesh.position.set(-aspect + 0.35, -0.6, 0);
            
            hudScene.add(earthMesh);
            resolve();
        };
        img.onerror = reject;
        img.src = mapUrl;
    });
};

const initScene = async () => {
  if (!canvasRef.value || !containerRef.value) return;

  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(props.isDark ? 0x000000 : 0xffffff, 0.03);
  
  camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 1.5, BASE_CAMERA_Z); 
  
  renderer = new THREE.WebGLRenderer({ canvas: canvasRef.value, alpha: true, antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio); 
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.autoClear = false; 
  renderer.shadowMap.enabled = true;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.enableZoom = false; 
  controls.enablePan = false;
  controls.mouseButtons = { LEFT: null as any, MIDDLE: null as any, RIGHT: THREE.MOUSE.ROTATE };

  hudScene = new THREE.Scene();
  const aspect = window.innerWidth / window.innerHeight;
  hudCamera = new THREE.OrthographicCamera(-aspect, aspect, 1, -1, 0.1, 10);
  hudCamera.position.z = 1;

  const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
  scene.add(ambientLight);
  const dirLight = new THREE.DirectionalLight(0xffffff, 2);
  dirLight.position.set(5, 10, 7);
  dirLight.castShadow = true;
  scene.add(dirLight);
  const fillLight = new THREE.PointLight(0x4455ff, 1);
  fillLight.position.set(-5, 2, 3);
  scene.add(fillLight);

  await initFloatingBackground();
  await createTexturedEarth(); 

  if (vscodeScreenRef.value && vscodeScreenRef.value.canvasRef) {
    const screenCanvas = vscodeScreenRef.value.canvasRef;
    screenTexture = new THREE.CanvasTexture(screenCanvas);
    screenTexture.flipY = false;
    screenTexture.colorSpace = THREE.SRGBColorSpace;
    screenTexture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    screenTexture.minFilter = THREE.LinearMipmapLinearFilter;
    screenTexture.magFilter = THREE.LinearFilter;
  }

  const loader = new GLTFLoader();
  loader.load('/models/Fullsetup.glb', (gltf) => {
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
      model.updateMatrixWorld(true);

      const targetMeshNames = ['Monitor_Cube_2']; 
      const pcCaseName = 'Computer_Cube'; 

      model.traverse((child) => {
        if ((child as THREE.Mesh).isMesh && targetMeshNames.includes(child.name) && screenTexture) {
            const mesh = child as THREE.Mesh;
            monitorMesh = mesh; 
            
            mesh.material = new THREE.MeshStandardMaterial({
              map: screenTexture,
              emissive: 0xffffff,
              emissiveMap: screenTexture,
              emissiveIntensity: 0.8,
              roughness: 0.1,
              metalness: 0.5,
              side: THREE.FrontSide,
            });
        }

        if (child.name === pcCaseName) {
            pcCaseObject = child;
            
            const caseBox = new THREE.Box3().setFromObject(child);
            const caseCenter = new THREE.Vector3();
            caseBox.getCenter(caseCenter);

            const hintTexture = createHintTexture("點擊開機 👆");
            const hintMaterial = new THREE.SpriteMaterial({ 
                map: hintTexture, 
                transparent: true,
                depthTest: false,
                depthWrite: false 
            });
            startHintSprite = new THREE.Sprite(hintMaterial);
            startHintSprite.scale.set(1.5, 0.375, 1); 
            
            startHintSprite.position.set(caseCenter.x, caseBox.max.y + 0.3, caseCenter.z);
            scene.add(startHintSprite);
        }
      });

      setupScrollAnimation(); 
    },
    undefined,
    (error) => console.error('模型載入失敗:', error)
  );
};

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

// === 修改後的 setupScrollAnimation ===
const setupScrollAnimation = () => {
  if (!monitorMesh) {
      console.warn("Monitor mesh not found for zoom effect.");
      return;
  }

  // 1. 改用 Bounding Box 計算螢幕的「幾何中心」
  // 這能解決原點在底部導致鏡頭偏低的問題
  const box = new THREE.Box3().setFromObject(monitorMesh);
  const screenCenter = new THREE.Vector3();
  box.getCenter(screenCenter);

  // 2. 設定相機最終位置
  // 以螢幕中心為基準，往 Z 軸拉出一段距離
  const endPos = screenCenter.clone();
  endPos.z += 0.6; // 稍微拉遠一點點 (0.6)，避免穿模穿得太生硬
  // endPos.y 保持與螢幕中心一致，這樣就是正視螢幕

  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: containerRef.value,
      start: "top top",
      end: "+=1500", 
      scrub: 1, 
      pin: true, 
      onLeave: () => {
          emit('enter-site');
          if (canvasRef.value) canvasRef.value.style.pointerEvents = 'none';
      },
      onEnterBack: () => {
          if (canvasRef.value) canvasRef.value.style.pointerEvents = 'auto';
      }
    }
  });

  tl.to(camera.position, { 
      x: endPos.x, 
      y: endPos.y, 
      z: endPos.z, 
      duration: 3, 
      ease: "power2.inOut" 
  })
  .to(controls.target, { 
      x: screenCenter.x, 
      y: screenCenter.y, 
      z: screenCenter.z, 
      duration: 3, 
      ease: "power2.inOut" 
  }, "<")
  .to(canvasRef.value, { opacity: 0, duration: 0.5 }, "-=0.5");
};

// ... (以下標準功能保持不變) ...
const onMouseMove = (event: MouseEvent) => {
    if (!canvasRef.value) return;
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    if (pcCaseObject && camera) {
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObject(pcCaseObject, true);
        const isInteracting = intersects.length > 0;
        
        if (isInteracting !== isHoveringPc) {
            isHoveringPc = isInteracting;
            canvasRef.value.style.cursor = isHoveringPc ? 'pointer' : 'default';
        }
    }
};

const onClick = () => {
    if (!isHoveringPc || !pcCaseObject || !vscodeScreenRef.value) return;
    if (vscodeScreenRef.value.isPoweredOn) return;

    vscodeScreenRef.value.turnOn();
    
    gsap.to(pcCaseObject.scale, {
        x: pcCaseObject.scale.x * 0.95,
        y: pcCaseObject.scale.y * 0.95,
        z: pcCaseObject.scale.z * 0.95,
        duration: 0.1,
        yoyo: true,
        repeat: 1
    });

    if (startHintSprite) {
        gsap.to(startHintSprite.material, {
            opacity: 0,
            duration: 0.5,
            onComplete: () => {
                if (startHintSprite) startHintSprite.visible = false;
            }
        });
    }
    
    if (canvasRef.value) canvasRef.value.style.cursor = 'default';
    isHoveringPc = false;
};

const animate = () => {
  animationId = requestAnimationFrame(animate);
  if (controls) controls.update();
  
  floatingElements.forEach(el => {
    el.sprite.position.add(el.velocity);
    const limit = 15;
    if (el.sprite.position.x > limit) el.sprite.position.x = -limit;
    if (el.sprite.position.x < -limit) el.sprite.position.x = limit;
    if (el.sprite.position.y > 10) el.sprite.position.y = -10;
    if (el.sprite.position.y < -10) el.sprite.position.y = 10;
  });

  if (earthMesh) earthMesh.rotation.y += 0.002; 
  if (screenTexture) screenTexture.needsUpdate = true;

  if (startHintSprite && startHintSprite.visible) {
      const time = Date.now() * 0.003;
      startHintSprite.position.y += Math.sin(time) * 0.0005; 
  }

  if (renderer && scene && camera && hudScene && hudCamera) {
      renderer.clear();
      renderer.render(scene, camera);
      renderer.clearDepth();
      renderer.render(hudScene, hudCamera);
  }
};

const handleResize = () => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const aspect = width / height;

  if (camera && renderer && hudCamera) {
    camera.aspect = aspect;
    camera.updateProjectionMatrix();
    
    hudCamera.left = -aspect;
    hudCamera.right = aspect;
    hudCamera.updateProjectionMatrix();

    if (earthMesh) {
       earthMesh.position.x = -aspect + 0.35;
       earthMesh.position.y = -0.6; 
    }

    renderer.setSize(width, height);
  }
};

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
  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('click', onClick);
});

onUnmounted(() => {
  cancelAnimationFrame(animationId);
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('wheel', handleWheel);
  window.removeEventListener('mousemove', onMouseMove);
  window.removeEventListener('click', onClick);

  ScrollTrigger.getAll().forEach(t => t.kill());
  if (renderer) renderer.dispose();
  if (controls) controls.dispose();
  if (screenTexture) screenTexture.dispose();
  
  floatingElements.forEach(el => {
    const material = el.sprite.material;
    if (!Array.isArray(material) && material.map) material.map.dispose();
    safeDisposeMaterial(material);
  });
  if (startHintSprite) {
      safeDisposeMaterial(startHintSprite.material);
      if (startHintSprite.material.map) startHintSprite.material.map.dispose();
  }
  if (earthMesh) {
    earthMesh.geometry.dispose();
    safeDisposeMaterial(earthMesh.material);
  }
});
</script>

<template>
  <div ref="containerRef" class="intro-container">
    <canvas ref="canvasRef" class="webgl-canvas"></canvas>
    <VscodeScreen ref="vscodeScreenRef" />
    <div class="scroll-hint">
      <p>Scroll Up to Zoom Out / Right Click to Rotate</p>
      <p>Scroll Down to Enter</p>
      <div class="arrow">⬇</div>
    </div>
  </div>
</template>

<style scoped>
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
  color: #D4D4D4;
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