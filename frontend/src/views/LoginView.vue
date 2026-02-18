<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
// 引入剛剛寫好的樣式
import '@/assets/css/login.css';

const router = useRouter();
const username = ref('');
const password = ref('');
const errorMsg = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  errorMsg.value = '';
  isLoading.value = true;

  // FastAPI 的 OAuth2PasswordRequestForm 需要用 FormData 傳送
  const formData = new FormData();
  formData.append('username', username.value);
  formData.append('password', password.value);

  try {
    const res = await axios.post('/api/login', formData);
    
    // 登入成功：把 Token 存在 sessionStorage
    sessionStorage.setItem('admin_token', res.data.access_token);
    
    // 稍微延遲一下讓使用者看到成功的狀態 (選用)
    setTimeout(() => {
        router.push('/admin'); // 跳轉到後台
    }, 500);

  } catch (error: any) {
    if (error.response && error.response.status === 429) {
      errorMsg.value = '錯誤次數過多，請稍後再試。';
    } else {
      errorMsg.value = '帳號或密碼錯誤';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <i class="fa-solid fa-user-secret"></i>
        <h2>後台管理系統</h2>
        <p>System Login</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label>管理員帳號</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="請輸入帳號" 
            required 
            autofocus 
          />
        </div>
        
        <div class="input-group">
          <label>通行密碼</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="請輸入密碼" 
            required 
          />
        </div>

        <div v-if="errorMsg" class="error-msg">
            <i class="fa-solid fa-circle-exclamation"></i>
            {{ errorMsg }}
        </div>

        <button type="submit" class="btn-submit" :disabled="isLoading">
          <span v-if="isLoading">
            <i class="fa-solid fa-spinner fa-spin"></i> 驗證中...
          </span>
          <span v-else>
            登入系統 <i class="fa-solid fa-arrow-right"></i>
          </span>
        </button>
      </form>
    </div>
  </div>
</template>