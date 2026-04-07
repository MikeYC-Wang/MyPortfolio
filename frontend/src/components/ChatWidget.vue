<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue';
import api from '@/api';
import { useToast } from 'vue-toastification';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const STORAGE_KEY = 'mike_chat_history_v1';
const MAX_HISTORY = 20;
const GREETING: ChatMessage = {
  role: 'assistant',
  content: '嗨！我是 Mike 的 AI 助手 🤖 想了解 Mike 的作品、技術背景、或聯絡方式嗎？問我吧！',
};

const toast = useToast();
const isOpen = ref(false);
const isLoading = ref(false);
const inputText = ref('');
const messages = ref<ChatMessage[]>([]);
const listRef = ref<HTMLDivElement | null>(null);

onMounted(() => {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        messages.value = parsed;
      }
    }
  } catch {}
});

watch(
  messages,
  (val) => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(val));
    } catch {}
  },
  { deep: true }
);

const scrollToBottom = async () => {
  await nextTick();
  if (listRef.value) {
    listRef.value.scrollTop = listRef.value.scrollHeight;
  }
};

const openWidget = () => {
  isOpen.value = true;
  if (messages.value.length === 0) {
    messages.value.push({ ...GREETING });
  }
  scrollToBottom();
};

const closeWidget = () => {
  isOpen.value = false;
};

const trimHistory = () => {
  if (messages.value.length > MAX_HISTORY) {
    messages.value = messages.value.slice(messages.value.length - MAX_HISTORY);
  }
};

const sendMessage = async () => {
  const text = inputText.value.trim();
  if (!text || isLoading.value) return;
  inputText.value = '';
  messages.value.push({ role: 'user', content: text });
  trimHistory();
  scrollToBottom();
  isLoading.value = true;
  try {
    const res = await api.post('/api/ai/chat', { messages: messages.value });
    const reply: string = res.data.reply ?? '';
    messages.value.push({ role: 'assistant', content: reply });
    trimHistory();
    scrollToBottom();
  } catch (error: any) {
    const status = error?.response?.status;
    if (status === 503) toast.error('AI 服務暫時不可用，請稍後再試');
    else if (status === 429) toast.error('請求太頻繁，請稍候');
    else toast.error('出錯了，請稍後再試');
  } finally {
    isLoading.value = false;
  }
};

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
};

const clearChat = () => {
  messages.value = [{ ...GREETING }];
};
</script>

<template>
  <div class="chat-widget-root">
    <transition name="chat-pop">
      <div v-if="isOpen" class="chat-panel">
        <div class="chat-header">
          <div class="chat-title">
            <i class="fa-solid fa-robot"></i>
            <span>問問 Mike 的 AI 助手</span>
          </div>
          <div class="chat-header-actions">
            <button class="chat-icon-btn" title="清除對話" @click="clearChat">
              <i class="fa-solid fa-rotate-right"></i>
            </button>
            <button class="chat-icon-btn" title="關閉" @click="closeWidget">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>

        <div ref="listRef" class="chat-messages">
          <div v-for="(msg, i) in messages" :key="i" class="chat-row" :class="msg.role">
            <div class="chat-avatar">
              <i class="fa-solid" :class="msg.role === 'user' ? 'fa-user' : 'fa-robot'"></i>
            </div>
            <div class="chat-bubble">{{ msg.content }}</div>
          </div>
          <div v-if="isLoading" class="chat-row assistant">
            <div class="chat-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="chat-bubble typing">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
              <span class="typing-text">Bot 正在輸入...</span>
            </div>
          </div>
        </div>

        <div class="chat-input-row">
          <textarea
            v-model="inputText"
            class="chat-input"
            rows="1"
            placeholder="輸入訊息..."
            :disabled="isLoading"
            @keydown="handleKeydown"
          ></textarea>
          <button class="chat-send-btn" :disabled="isLoading || !inputText.trim()" @click="sendMessage">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </transition>

    <button v-if="!isOpen" class="chat-bubble-btn" @click="openWidget" title="打開 AI 助手">
      <i class="fa-solid fa-comments"></i>
    </button>
  </div>
</template>

<style scoped>
.chat-widget-root {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 9999;
  font-family: inherit;
}

.chat-bubble-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00f2ff, #0066ff);
  color: #fff;
  border: none;
  font-size: 1.6rem;
  cursor: pointer;
  box-shadow: 0 6px 24px rgba(0, 242, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}
.chat-bubble-btn:hover { transform: scale(1.08) rotate(-4deg); }

.chat-panel {
  width: 350px;
  height: 500px;
  background: rgba(15, 20, 30, 0.96);
  backdrop-filter: blur(15px);
  border: 1px solid #00f2ff44;
  border-radius: 14px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 242, 255, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #e6f5ff;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: rgba(0, 242, 255, 0.08);
  border-bottom: 1px solid #00f2ff33;
}
.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 0.95rem;
  color: #00f2ff;
}
.chat-header-actions { display: flex; gap: 4px; }
.chat-icon-btn {
  background: transparent;
  border: none;
  color: #e6f5ff;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.chat-icon-btn:hover { background: rgba(0, 242, 255, 0.15); color: #00f2ff; }

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scrollbar-width: thin;
  scrollbar-color: #00f2ff44 transparent;
}
.chat-messages::-webkit-scrollbar { width: 6px; }
.chat-messages::-webkit-scrollbar-thumb { background: #00f2ff44; border-radius: 4px; }

.chat-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
.chat-row.user { flex-direction: row-reverse; }

.chat-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(0, 242, 255, 0.15);
  border: 1px solid #00f2ff55;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00f2ff;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.chat-row.user .chat-avatar {
  background: rgba(0, 102, 255, 0.2);
  color: #58a6ff;
  border-color: #58a6ff66;
}

.chat-bubble {
  max-width: 75%;
  padding: 9px 12px;
  border-radius: 12px;
  background: rgba(0, 242, 255, 0.08);
  border: 1px solid #00f2ff22;
  font-size: 0.88rem;
  line-height: 1.55;
  white-space: pre-wrap;
  word-wrap: break-word;
}
.chat-row.user .chat-bubble {
  background: rgba(88, 166, 255, 0.18);
  border-color: #58a6ff44;
}

.chat-bubble.typing {
  display: flex;
  align-items: center;
  gap: 4px;
  font-style: italic;
  color: #99ccdd;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00f2ff;
  animation: dotPulse 1.2s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
.typing-text { margin-left: 6px; font-size: 0.78rem; }
@keyframes dotPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1.1); }
}

.chat-input-row {
  display: flex;
  gap: 8px;
  padding: 10px;
  border-top: 1px solid #00f2ff33;
  background: rgba(0, 0, 0, 0.25);
}
.chat-input {
  flex: 1;
  resize: none;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid #00f2ff33;
  border-radius: 8px;
  padding: 8px 10px;
  color: #e6f5ff;
  font-family: inherit;
  font-size: 0.88rem;
  outline: none;
  max-height: 80px;
}
.chat-input:focus { border-color: #00f2ff; }
.chat-send-btn {
  background: linear-gradient(135deg, #00f2ff, #0066ff);
  color: #fff;
  border: none;
  border-radius: 8px;
  width: 40px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: opacity 0.2s;
}
.chat-send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.chat-pop-enter-active, .chat-pop-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
  transform-origin: bottom right;
}
.chat-pop-enter-from, .chat-pop-leave-to {
  transform: scale(0.85) translateY(20px);
  opacity: 0;
}

@media (max-width: 480px) {
  .chat-panel { width: calc(100vw - 32px); height: 70vh; }
}
</style>
