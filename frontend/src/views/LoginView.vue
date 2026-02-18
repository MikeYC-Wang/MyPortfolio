<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

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
    
    // 登入成功：把 Token 存在 sessionStorage (關閉瀏覽器就失效，符合你的要求)
    sessionStorage.setItem('admin_token', res.data.access_token);
    
    alert('登入成功！');
    router.push('/admin'); // 跳轉到後台

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
      <div class="hacker-header">
        <i class="fa-solid fa-shield-halved"></i> SYSTEM LOGIN
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label>IDENTITY</label>
          <input v-model="username" type="text" placeholder="Username" required autofocus />
        </div>
        
        <div class="input-group">
          <label>PASSPHRASE</label>
          <input v-model="password" type="password" placeholder="Password" required />
        </div>

        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

        <button type="submit" :disabled="isLoading">
          <span v-if="isLoading">AUTHENTICATING...</span>
          <span v-else>ACCESS REQUEST</span>
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #0d0d0d;
  color: #fff;
}

.login-box {
  width: 350px;
  padding: 40px;
  background: rgba(30, 30, 30, 0.8);
  border: 1px solid #333;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  text-align: center;
}

.hacker-header {
  font-size: 1.5rem;
  font-weight: bold;
  color: #00ff00; /* Hacker Green */
  margin-bottom: 30px;
  letter-spacing: 2px;
  border-bottom: 1px solid #333;
  padding-bottom: 15px;
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

.input-group label {
  display: block;
  font-size: 0.8rem;
  color: #888;
  margin-bottom: 5px;
  font-family: 'Fira Code', monospace;
}

.input-group input {
  width: 100%;
  padding: 12px;
  background: #111;
  border: 1px solid #444;
  color: #fff;
  border-radius: 4px;
  outline: none;
  font-family: 'Fira Code', monospace;
  transition: 0.3s;
}
.input-group input:focus { border-color: #00ff00; }

button {
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  letter-spacing: 1px;
  margin-top: 10px;
  transition: 0.2s;
}
button:hover { background: #0056b3; }
button:disabled { background: #555; cursor: not-allowed; }

.error-msg {
  color: #ff4d4d;
  font-size: 0.9rem;
  margin-bottom: 15px;
  background: rgba(255, 77, 77, 0.1);
  padding: 8px;
  border-radius: 4px;
}
</style>