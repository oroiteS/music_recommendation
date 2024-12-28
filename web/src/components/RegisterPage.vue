<template>
    <div class="register-container">
        <div class="register-box">
            <h2>注册</h2>
            <form @submit.prevent="handleRegister">
                <div class="input-group">
                    <label for="login_id">登录账号</label>
                    <input 
                        type="text" 
                        id="login_id" 
                        v-model="login_id" 
                        placeholder="请输入登录账号（仅限英文字母和数字）" 
                        required 
                        pattern="[a-zA-Z0-9]+" 
                    />
                </div>
                <div class="input-group">
                    <label for="username">用户名</label>
                    <input 
                        type="text" 
                        id="username" 
                        v-model="username" 
                        placeholder="请输入用户名" 
                        required 
                    />
                </div>
                <div class="input-group">
                    <label for="password">密码</label>
                    <input 
                        type="password" 
                        id="password" 
                        v-model="password" 
                        placeholder="请输入密码（至少6位）" 
                        required 
                        minlength="6" 
                    />
                </div>
                <div class="input-group">
                    <label for="confirm_password">确认密码</label>
                    <input 
                        type="password" 
                        id="confirm_password" 
                        v-model="confirm_password" 
                        placeholder="请确认密码" 
                        required 
                    />
                </div>
                <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
                <button type="submit" class="btn-register">注册</button>
            </form>
            <div class="login-link">
                <span>已有账户？</span>
                <router-link to="/login">登录</router-link>
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
            username: '',
            password: '',
            confirm_password: '',
            errorMessage: ''
        };
    },
    methods: {
        async handleRegister() {
            // 验证密码
            if (this.password !== this.confirm_password) {
                this.errorMessage = '两次输入的密码不一致';
                return;
            }

            if (this.password.length < 6) {
                this.errorMessage = '密码长度不能少于6位';
                return;
            }

            // 验证登录账号格式
            if (!/^[a-zA-Z0-9]+$/.test(this.login_id)) {
                this.errorMessage = '登录账号只能包含字母和数字';
                return;
            }

            try {
                const response = await axios.post('http://localhost:5000/auth/register', {
                    login_id: this.login_id,
                    username: this.username,
                    password: this.password
                });

                if (response.data.success) {
                    alert('注册成功！');
                    this.$router.push('/login');
                } else {
                    this.errorMessage = response.data.message;
                }
            } catch (error) {
                this.errorMessage = '注册失败，请稍后重试';
                console.error(error);
            }
        }
    }
};
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f4f7fc;
}

.register-box {
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

.btn-register {
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

.btn-register:hover {
    background-color: #2a61c5;
}

.error-message {
    color: #ff4d4d;
    text-align: center;
    margin-top: 10px;
}

.login-link {
    text-align: center;
    margin-top: 15px;
}

.login-link span {
    color: #888;
}

.login-link a {
    color: #4f81e4;
    text-decoration: none;
    font-weight: bold;
}
</style>