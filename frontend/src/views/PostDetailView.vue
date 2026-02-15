<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

const route = useRoute();
const router = useRouter();
const post = ref<any>(null);
const loading = ref(true);

// 建立一個獨立的 HTML 跳脫字元函式，避免在建構式中參照 md 實例
const escapeHtml = (unsafe: string): string => {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};

// 初始化 Markdown 解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  // 這裡明確指定參數型別為 string
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }
    // 使用上方定義的 escapeHtml 替代 md.utils.escapeHtml
    return '<pre class="hljs"><code>' + escapeHtml(str) + '</code></pre>';
  }
});

onMounted(async () => {
  try {
    const res = await axios.get(`/api/posts/${route.params.id}`);
    post.value = res.data;
  } catch (error) {
    console.error('文章讀取失敗', error);
    router.push('/blog');
  } finally {
    loading.value = false;
  }
});
</script>