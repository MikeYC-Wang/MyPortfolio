<script setup lang="ts">
import { ref } from 'vue';
// import axios from 'axios';
import axios from '@/api';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import '@/assets/css/login.css';
import '@/assets/css/Theme.css';
import SiteFooter from '@/components/SiteFooter.vue';

const router = useRouter();
const toast = useToast();

const username = ref('');
const password = ref('');
const errorMsg = ref('');
const isLoading = ref(false);
const showPassword = ref(false);

const handleLogin = async () => {
  errorMsg.value = '';
  isLoading.value = true;

  const formData = new FormData();
  formData.append('username', username.value);
  formData.append('password', password.value);

  try {
    const res = await axios.post('/api/login', formData);
    sessionStorage.setItem('admin_token', res.data.access_token);

    toast.success('登入成功！'); 
    setTimeout(() => { router.push('/admin'); }, 500);
    
  } catch (error: any) {
    if (error.response && error.response.status === 429) {
      errorMsg.value = '錯誤次數過多，請稍後再試。';
      toast.error('錯誤次數過多，請稍後再試。');
    } else {
      errorMsg.value = '帳號或密碼錯誤';
      toast.error('登入失敗，請確認帳號密碼。');
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div>
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
          
          <div class="input-group password-group">
            <label>密碼</label>
            <div class="password-wrapper">
              <input 
                v-model="password" 
                :type="showPassword ? 'text' : 'password'" 
                placeholder="請輸入密碼" 
                required 
              />
              <button 
                type="button" 
                class="btn-eye" 
                @click="showPassword = !showPassword"
                tabindex="-1"
              >
                <i class="fa-solid" :class="showPassword ? 'fa-eye-slash' : 'fa-eye'"></i>
              </button>
            </div>
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
    <SiteFooter />
  </div>
</template>