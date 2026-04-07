<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from '@/api';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';
import SiteFooter from '@/components/SiteFooter.vue';
import { useToast } from 'vue-toastification'; // 引入 Toast 提示

const route = useRoute();
const router = useRouter();
const toast = useToast();
const post = ref<any>(null);
const loading = ref(true);
const apiBase = import.meta.env.VITE_API_BASE_URL || '';
const getCoverUrl = (img: string) => img.startsWith('http') ? img : `${apiBase}${img}`;

const escapeHtml = (unsafe: string): string => {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str: string, lang: string): string {
    let codeHtml = '';
    if (lang && hljs.getLanguage(lang)) {
      try {
        codeHtml = hljs.highlight(str, { language: lang, ignoreIllegals: true }).value;
      } catch (__) {}
    }
    if (!codeHtml) {
      codeHtml = escapeHtml(str);
    }

    return `
      <div class="code-block-wrapper">
        <button class="copy-btn" aria-label="Copy code">
          <i class="fa-regular fa-copy"></i>
        </button>
        <pre class="hljs"><code>${codeHtml}</code></pre>
      </div>
    `;
  }
});

const handleContentClick = async (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  // 判斷點擊的是不是 copy-btn (或者是按鈕裡面的 icon)
  const btn = target.closest('.copy-btn') as HTMLButtonElement;
  
  if (!btn) return; // 如果點的不是複製按鈕，就不理他
  
  const wrapper = btn.closest('.code-block-wrapper');
  if (!wrapper) return;
  
  const codeBlock = wrapper.querySelector('code');
  if (!codeBlock) return;
  
  try {
    // 呼叫瀏覽器原生剪貼簿 API 寫入程式碼
    await navigator.clipboard.writeText(codeBlock.innerText);
    
    // 按鈕視覺回饋：變成打勾
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check"></i> 成功';
    btn.classList.add('copied');
    toast.success('程式碼已複製到剪貼簿！');
    
    // 2 秒後恢復原狀
    setTimeout(() => {
      btn.innerHTML = originalHtml;
      btn.classList.remove('copied');
    }, 2000);
    
  } catch (err) {
    console.error('複製失敗', err);
    toast.error('複製失敗，請手動選取複製');
  }
};

// ============ TOC (Table of Contents) ============
interface TocItem { id: string; text: string; level: number; }
const toc = ref<TocItem[]>([]);
const activeId = ref<string>('');
let observer: IntersectionObserver | null = null;
let scrollHandler: (() => void) | null = null;
let trackedHeadings: HTMLElement[] = [];

const cleanupObserver = () => {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
  if (scrollHandler) {
    window.removeEventListener('scroll', scrollHandler);
    scrollHandler = null;
  }
  trackedHeadings = [];
};

// 從目前所有 heading 中，找到「最後一個 top <= 觸發線」的那個
// 觸發線設在視窗高度的 50% 處（章節標題滾到畫面正中央才高亮）
const updateActiveByScroll = () => {
  if (trackedHeadings.length === 0) return;
  const triggerY = window.innerHeight * 0.5;
  let currentId = trackedHeadings[0]!.id;
  for (const h of trackedHeadings) {
    const top = h.getBoundingClientRect().top;
    if (top <= triggerY) {
      currentId = h.id;
    } else {
      break;
    }
  }
  if (activeId.value !== currentId) {
    activeId.value = currentId;
  }
};

const buildToc = async () => {
  await nextTick();
  cleanupObserver();
  toc.value = [];
  const contentEl = document.querySelector('.post-detail-container .content');
  if (!contentEl) return;
  const headings = contentEl.querySelectorAll('h2, h3');
  const items: TocItem[] = [];
  headings.forEach((h, idx) => {
    if (!h.id) {
      h.id = `heading-${idx}`;
    }
    items.push({
      id: h.id,
      text: h.textContent || '',
      level: h.tagName === 'H2' ? 2 : 3,
    });
  });
  toc.value = items;

  if (items.length === 0) return;

  // 用 scroll handler + getBoundingClientRect 的「最近上方」演算法，比 IntersectionObserver 多個交集穩定
  trackedHeadings = Array.from(headings) as HTMLElement[];
  scrollHandler = () => {
    requestAnimationFrame(updateActiveByScroll);
  };
  window.addEventListener('scroll', scrollHandler, { passive: true });
  // 初始呼叫一次取得目前位置
  updateActiveByScroll();
};

const scrollToHeading = (id: string) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

watch(() => post.value?.content, () => {
  if (post.value?.content) buildToc();
});

onMounted(async () => {
  try {
    const res = await axios.get(`/api/posts/${route.params.id}`);
    post.value = res.data;
  } catch (error) {
    console.error('文章讀取失敗', error);
    router.push('/blog');
    return;
  } finally {
    loading.value = false;
  }
  // 必須在 loading 變 false、article 元素 render 出來之後才能掃 .content
  await buildToc();
});

onBeforeUnmount(() => {
  cleanupObserver();
});
</script>

<template>
  <div>
    <div class="post-detail-container">
      <div v-if="loading" class="loading-state">
        <i class="fa-solid fa-spinner fa-spin"></i> Loading...
      </div>
      
      <article v-else-if="post" class="markdown-body" @click="handleContentClick">
        <RouterLink to="/blog" class="back-link">
           <i class="fa-solid fa-arrow-left"></i> 回列表
        </RouterLink>

        <div class="post-header">
          <h1>{{ post.title }}</h1>
        </div>
        
        <img 
          v-if="post.cover_image" 
          :src="getCoverUrl(post.cover_image)"
          class="main-cover" 
        />

        <div class="content" v-html="md.render(post.content || '')"></div>
      </article>

      <div v-else class="error-state">
        文章載入錯誤或不存在。
      </div>
    </div>

    <aside v-if="toc.length > 0" class="toc-sidebar" aria-label="目錄">
      <div class="toc-title">目錄</div>
      <ul class="toc-list">
        <li
          v-for="item in toc"
          :key="item.id"
          :class="['toc-item', `toc-level-${item.level}`, { active: activeId === item.id }]"
          @click="scrollToHeading(item.id)"
        >
          {{ item.text }}
        </li>
      </ul>
    </aside>
    <SiteFooter />
  </div>
</template>

<style scoped>
.post-detail-container { 
  max-width: 800px; 
  margin: 0 auto; 
  padding: 4rem 2rem; 
  color: var(--text-color);
  position: relative; /* 關鍵：讓絕對定位參考此容器 */
  z-index: 10; 
  min-height: 80vh;
}

.loading-state, .error-state {
  text-align: center;
  font-size: 1.5rem;
  margin-top: 50px;
  color: var(--link-color);
}

.post-header { margin-bottom: 2rem; text-align: center; margin-top: 1rem; }
h1 { font-size: 2.5rem; margin-bottom: 1rem; color: var(--text-color); }
.main-cover { width: 100%; border-radius: 12px; margin-bottom: 3rem; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }

/* ✨ 修改後的返回按鈕樣式 */
.back-link { 
  position: absolute; 
  top: 20px;          
  left: 20px;         
  
  display: inline-flex; 
  align-items: center; 
  gap: 5px; 
  color: var(--link-color); 
  text-decoration: none; 
  font-size: 0.9rem; 
  transition: 0.3s;
}

.back-link:hover { color: var(--link-active); transform: translateX(-5px); }

/* RWD: 手機版如果太窄，讓按鈕回到正常流向，不然會蓋到標題 */
@media (max-width: 600px) {
  .back-link {
    position: static;
    display: block;
    margin-bottom: 10px;
  }
}

/* ==========================================
   Floating TOC Sidebar
========================================== */
.toc-sidebar {
  position: fixed;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  width: 240px;
  max-width: 240px;
  max-height: 70vh;
  overflow-y: auto;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  z-index: 20;
}

.toc-title {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 10px;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--text-secondary);
  padding: 6px 0 6px 0;
  line-height: 1.4;
  border-left: 2px solid transparent;
  padding-left: 10px;
  transition: color 0.2s ease, background 0.2s ease, border-color 0.2s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.toc-item:hover {
  color: var(--text-color);
  background: var(--btn-hover);
  border-radius: 4px;
}

.toc-level-3 {
  padding-left: 24px;
  font-size: 0.82rem;
}

.toc-item.active {
  color: var(--milk-tea);
  font-weight: 700;
  border-left: 2px solid var(--milk-tea);
}

.toc-level-3.active {
  padding-left: 24px;
}

@media (max-width: 1024px) {
  .toc-sidebar {
    display: none;
  }
}

/* ==========================================
   Markdown 基礎排版樣式
========================================== */
:deep(.content) { line-height: 1.8; font-size: 1.1rem; }
:deep(h1), :deep(h2), :deep(h3) { margin-top: 2rem; margin-bottom: 1rem; color: var(--link-active); }
:deep(p) { margin-bottom: 1.5rem; color: var(--text-color); opacity: 0.9; }
:deep(code) { font-family: 'Fira Code', monospace; }
:deep(a) { color: #58a6ff; text-decoration: none; }
:deep(a:hover) { text-decoration: underline; }
:deep(ul), :deep(ol) { padding-left: 1.5rem; margin-bottom: 1.5rem; }
:deep(li) { margin-bottom: 0.5rem; }
:deep(blockquote) { border-left: 4px solid var(--link-active); padding-left: 1rem; color: #8b949e; margin: 1.5rem 0; }
:deep(img) { max-width: 100%; border-radius: 8px; }

/* ==========================================
   程式碼區塊樣式美化 (Mac 視窗風格 + 複製按鈕)
========================================== */
/* 程式碼外層容器 */
:deep(.code-block-wrapper) {
  position: relative;
  border-radius: 8px;
  background: #282c34;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

/* 模擬 Mac 的三個小圓點 */
:deep(.code-block-wrapper::before) {
  content: '';
  position: absolute;
  top: 15px;
  left: 15px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ff5f56;
  box-shadow: 20px 0 0 #ffbd2e, 40px 0 0 #27c93f;
  z-index: 1;
}

:deep(.code-block-wrapper pre) {
  margin: 0 !important;
  padding: 0px 20px 20px 20px !important; 
  background: transparent !important; 
  border-radius: 0;
  overflow-x: auto;
  line-height: 1.6;
}
:deep(.code-block-wrapper pre::-webkit-scrollbar) {
  height: 8px; /* 捲軸高度 */
}
:deep(.code-block-wrapper code) {
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
  display: block; 
}

/* 複製按鈕樣式 */
:deep(.copy-btn) {
  position: absolute;
  top: 8px;
  right: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #aaa;
  height: 30px; 
  padding: 0 12px; 
  display: inline-flex;
  align-items: center; 
  justify-content: center; 
  /* 👈 修改 3：移除 line-height: 1，讓 flexbox 自然垂直置中字體與 icon */
  border-radius: 6px;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  gap: 6px;
  transition: all 0.2s ease;
  z-index: 2;
}

:deep(.copy-btn:hover) {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

/* 點擊成功後的按鈕狀態 */
:deep(.copy-btn.copied) {
  background: var(--milk-tea-dark, #d4b595);
  color: #121212;
  border-color: transparent;
  font-weight: bold;
}
</style>