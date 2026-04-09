<script setup lang="ts">
import { ref } from 'vue';
import api from '@/api';
import { useToast } from 'vue-toastification';

type AiAction = 'polish' | 'translate_en' | 'summarize' | 'title_suggestions';

const props = defineProps<{
  getText: () => string;
  getTitle: () => string;
  setText: (s: string) => void;
  setTitle: (s: string) => void;
  modeLabel: string; // e.g. "文章" / "專案"
}>();

const toast = useToast();
const isOpen = ref(false);
const aiLoading = ref<AiAction | null>(null);
const aiSummary = ref('');
const aiTitleSuggestions = ref<string[]>([]);

// 待套用的修改 (潤稿 / 翻譯) — 給使用者預覽再決定要不要 apply
interface PendingChange {
  action: 'polish' | 'translate_en';
  original: string;
  proposed: string;
}
const pendingChange = ref<PendingChange | null>(null);
const showOriginal = ref(false);

const applyPendingChange = () => {
  if (!pendingChange.value) return;
  props.setText(pendingChange.value.proposed);
  toast.success('已套用變更');
  pendingChange.value = null;
  showOriginal.value = false;
};

const discardPendingChange = () => {
  pendingChange.value = null;
  showOriginal.value = false;
  toast.info('已捨棄變更');
};

const togglePanel = () => {
  isOpen.value = !isOpen.value;
};

const runAiAction = async (action: AiAction) => {
  const text = action === 'title_suggestions' ? props.getTitle() : props.getText();
  if (!text || !text.trim()) {
    toast.warning(action === 'title_suggestions' ? '請先輸入標題' : '請先輸入內容');
    return;
  }
  aiLoading.value = action;
  try {
    const res = await api.post('/api/ai/assist', { text, action });
    const result: string = res.data.result ?? '';
    if (action === 'polish' || action === 'translate_en') {
      pendingChange.value = { action, original: text, proposed: result };
      showOriginal.value = false;
      toast.success(action === 'polish' ? '潤稿完成，請預覽後決定是否套用' : '翻譯完成，請預覽後決定是否套用');
    } else if (action === 'summarize') {
      aiSummary.value = result;
      try { await navigator.clipboard.writeText(result); } catch {}
      toast.success('摘要已生成（已複製到剪貼簿）');
    } else if (action === 'title_suggestions') {
      aiTitleSuggestions.value = result
        .split('\n')
        .map((s) => s.replace(/^[\s\-\d\.、）)]+/, '').trim())
        .filter((s) => s.length > 0)
        .slice(0, 8);
      toast.success('已生成標題建議');
    }
  } catch (error: any) {
    const status = error?.response?.status;
    if (status === 503) toast.error('AI 服務暫時不可用，請稍後再試');
    else if (status === 429) toast.error('請求太頻繁，請稍候');
    else if (status === 401) toast.error('請重新登入');
    else toast.error('AI 操作失敗，請稍後再試');
  } finally {
    aiLoading.value = null;
  }
};

const applyTitleSuggestion = (s: string) => {
  props.setTitle(s);
  aiTitleSuggestions.value = [];
};
</script>

<template>
  <div class="admin-ai-root">
    <!-- Floating button -->
    <button v-if="!isOpen" class="ai-bubble-btn" @click="togglePanel" title="Claude AI 助手">
      <svg class="claude-logo" viewBox="0 0 24 24" aria-hidden="true">
        <g stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <line x1="12" y1="2.5" x2="12" y2="21.5"/>
          <line x1="2.5" y1="12" x2="21.5" y2="12"/>
          <line x1="5.2" y1="5.2" x2="18.8" y2="18.8"/>
          <line x1="18.8" y1="5.2" x2="5.2" y2="18.8"/>
        </g>
      </svg>
    </button>

    <!-- Panel -->
    <transition name="ai-pop">
      <div v-if="isOpen" class="ai-panel-card">
        <div class="ai-header">
          <div class="ai-title">
            <svg class="claude-logo small" viewBox="0 0 24 24" aria-hidden="true">
              <g stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <line x1="12" y1="2.5" x2="12" y2="21.5"/>
                <line x1="2.5" y1="12" x2="21.5" y2="12"/>
                <line x1="5.2" y1="5.2" x2="18.8" y2="18.8"/>
                <line x1="18.8" y1="5.2" x2="5.2" y2="18.8"/>
              </g>
            </svg>
            <span>Claude AI 助手</span>
            <span class="mode-tag">{{ modeLabel }}</span>
          </div>
          <button class="ai-close" @click="togglePanel" title="收起">&times;</button>
        </div>

        <div class="ai-actions">
          <button class="ai-action-btn" :disabled="aiLoading !== null" @click="runAiAction('polish')">
            <i class="fa-solid" :class="aiLoading === 'polish' ? 'fa-spinner fa-spin' : 'fa-feather'"></i>
            <span>潤稿</span>
          </button>
          <button class="ai-action-btn" :disabled="aiLoading !== null" @click="runAiAction('translate_en')">
            <i class="fa-solid" :class="aiLoading === 'translate_en' ? 'fa-spinner fa-spin' : 'fa-language'"></i>
            <span>翻譯英文</span>
          </button>
          <button class="ai-action-btn" :disabled="aiLoading !== null" @click="runAiAction('summarize')">
            <i class="fa-solid" :class="aiLoading === 'summarize' ? 'fa-spinner fa-spin' : 'fa-align-left'"></i>
            <span>生成摘要</span>
          </button>
          <button class="ai-action-btn" :disabled="aiLoading !== null" @click="runAiAction('title_suggestions')">
            <i class="fa-solid" :class="aiLoading === 'title_suggestions' ? 'fa-spinner fa-spin' : 'fa-lightbulb'"></i>
            <span>標題建議</span>
          </button>
        </div>

        <div v-if="pendingChange" class="ai-result pending">
          <div class="ai-result-title">
            <span>{{ pendingChange.action === 'polish' ? '潤稿後預覽' : '英文翻譯預覽' }}</span>
            <button class="ai-clear" @click="showOriginal = !showOriginal">
              {{ showOriginal ? '看修改後' : '看原文' }}
            </button>
          </div>
          <div class="ai-preview-body">{{ showOriginal ? pendingChange.original : pendingChange.proposed }}</div>
          <div class="ai-preview-actions">
            <button class="ai-btn-apply" @click="applyPendingChange">
              <i class="fa-solid fa-check"></i> 套用變更
            </button>
            <button class="ai-btn-discard" @click="discardPendingChange">
              <i class="fa-solid fa-xmark"></i> 捨棄
            </button>
          </div>
        </div>

        <div v-if="aiTitleSuggestions.length" class="ai-result">
          <div class="ai-result-title">
            <span>標題建議</span>
            <button class="ai-clear" @click="aiTitleSuggestions = []">清除</button>
          </div>
          <div class="ai-chip-list">
            <button v-for="(s, i) in aiTitleSuggestions" :key="i" class="ai-chip" @click="applyTitleSuggestion(s)">{{ s }}</button>
          </div>
        </div>

        <div v-if="aiSummary" class="ai-result">
          <div class="ai-result-title">
            <span>AI 摘要</span>
            <button class="ai-clear" @click="aiSummary = ''">清除</button>
          </div>
          <div class="ai-summary-body">{{ aiSummary }}</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.admin-ai-root {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 9998;
  font-family: inherit;
}

.claude-logo {
  width: 26px;
  height: 26px;
  color: var(--bg-color);
  flex-shrink: 0;
}
.claude-logo.small { width: 18px; height: 18px; color: var(--milk-tea); }

.ai-bubble-btn {
  width: 58px;
  height: 58px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--milk-tea), var(--milk-tea-dark));
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.ai-bubble-btn:hover {
  transform: scale(1.08) rotate(8deg);
  box-shadow: var(--card-hover-shadow);
}

.ai-panel-card {
  width: 340px;
  max-height: 70vh;
  overflow-y: auto;
  background: var(--card-bg);
  backdrop-filter: blur(15px);
  border: 1px solid var(--card-border);
  border-radius: 14px;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  color: var(--text-color);
  scrollbar-width: thin;
  scrollbar-color: var(--milk-tea-dark) transparent;
}
.ai-panel-card::-webkit-scrollbar { width: 6px; }
.ai-panel-card::-webkit-scrollbar-thumb { background: var(--milk-tea-dark); border-radius: 4px; }

.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  border-radius: 14px 14px 0 0;
}
.ai-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 0.95rem;
  color: var(--text-color);
}
.mode-tag {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--milk-tea);
  color: var(--bg-color);
  margin-left: 4px;
}
.ai-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 1.4rem;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  line-height: 1;
}
.ai-close:hover { background: var(--btn-hover); color: var(--milk-tea); }

.ai-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 14px;
}
.ai-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 8px;
  background: var(--btn-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-color);
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.ai-action-btn:hover:not(:disabled) {
  background: var(--milk-tea);
  border-color: var(--milk-tea);
  color: var(--bg-color);
  transform: translateY(-1px);
}
.ai-action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.ai-action-btn i { font-size: 0.95rem; }

.ai-result {
  margin: 0 14px 14px;
  padding: 12px;
  background: var(--btn-bg);
  border: 1px dashed var(--border-color);
  border-radius: 8px;
}
.ai-result-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  font-weight: bold;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.ai-clear {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  cursor: pointer;
}
.ai-clear:hover { color: var(--milk-tea); border-color: var(--milk-tea); }

.ai-summary-body,
.ai-preview-body {
  white-space: pre-wrap;
  line-height: 1.7;
  font-size: 0.85rem;
  color: var(--text-color);
  max-height: 220px;
  overflow-y: auto;
  padding: 4px 2px;
  scrollbar-width: thin;
}

.ai-result.pending {
  border-style: solid;
  border-color: var(--milk-tea);
  background: var(--bg-secondary);
}

.ai-preview-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.ai-btn-apply,
.ai-btn-discard {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.ai-btn-apply {
  background: var(--milk-tea);
  color: var(--bg-color);
  border: 1px solid var(--milk-tea);
  font-weight: bold;
}
.ai-btn-apply:hover {
  background: var(--milk-tea-dark);
  border-color: var(--milk-tea-dark);
}
.ai-btn-discard {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}
.ai-btn-discard:hover {
  border-color: var(--text-color);
  color: var(--text-color);
}

.ai-chip-list { display: flex; flex-wrap: wrap; gap: 6px; }
.ai-chip {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 5px 10px;
  border-radius: 14px;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: inherit;
  transition: all 0.15s;
}
.ai-chip:hover { border-color: var(--milk-tea); color: var(--milk-tea); }

.ai-pop-enter-active, .ai-pop-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
  transform-origin: bottom right;
}
.ai-pop-enter-from, .ai-pop-leave-to {
  transform: scale(0.85) translateY(20px);
  opacity: 0;
}

@media (max-width: 480px) {
  .ai-panel-card { width: calc(100vw - 32px); }
}
</style>
