<template>
  <div class="login-container">
    <div class="login-box">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="login_id">登录账号</label>
          <input 
            type="text" 
            id="login_id" 
            v-model.trim="login_id" 
            placeholder="请输入登录账号" 
            required 
          />
        </div>
        <div class="input-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model.trim="password" 
            placeholder="请输入密码" 
            required 
          />
        </div>
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <button type="submit" class="btn-login">登录</button>
      </form>
      <div class="signup-link">
        <span>还没有账户？</span>
        <router-link to="/register">注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      login_id: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    async handleLogin() {
      // 添加前端验证
      if (!this.login_id || !this.password) {
        this.errorMessage = '用户名和密码不能为空';
        return;
      }

      try {
        // 打印请求数据，用于调试
        console.log('发送的数据:', {
          login_id: this.login_id,
          password: this.password
        });

        const response = await axios.post('http://localhost:5000/auth/login', {
          login_id: this.login_id,
          password: this.password
        });

        // 打印响应数据，用于调试
        console.log('服务器响应:', response.data);

        if (response.data.success) {
          sessionStorage.setItem('user', JSON.stringify(response.data.user));
          this.$router.push('/');
        } else {
          this.errorMessage = response.data.message;
        }
      } catch (error) {
        console.error('登录错误:', error);
        this.errorMessage = error.response?.data?.message || '登录失败，请稍后重试';
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f4f7fc;
}

.login-box {
  width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.input-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
}

.input-group input:focus {
  border-color: #4f81e4;
  outline: none;
}

.btn-login {
  width: 100%;
  padding: 12px;
  background-color: #4f81e4;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-login:hover {
  background-color: #2a61c5;
}

.signup-link {
  text-align: center;
  margin-top: 15px;
}

.signup-link span {
  color: #888;
}

.signup-link a {
  color: #4f81e4;
  text-decoration: none;
  font-weight: bold;
}
</style>