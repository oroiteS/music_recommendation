<template>
  <div class="my-page">
    <!-- 用户基本信息卡片 -->
    <div class="card user-info">
      <div class="user-header">
        <h2>个人信息</h2>
        <div class="user-identity" :class="{ admin: user.user_identity === 1 }">
          {{ user.user_identity === 1 ? '管理员' : '普通用户' }}
        </div>
      </div>
      <div class="info-content">
        <div class="info-item">
          <label>用户名：</label>
          <div v-if="!isEditingUsername" class="username-display">
            <span>{{ user.username }}</span>
            <button class="btn-edit" @click="startEditUsername">修改</button>
          </div>
          <div v-else class="username-edit">
            <input v-model="newUsername" type="text" />
            <button class="btn-save" @click="saveUsername">保存</button>
            <button class="btn-cancel" @click="cancelEditUsername">取消</button>
          </div>
        </div>
        <div class="info-item">
          <button class="btn-change-password" @click="showChangePassword = true">
            修改密码
          </button>
        </div>
      </div>
    </div>

    <!-- 音乐喜好设置卡片 -->
    <div class="card preferences">
      <h2>音乐喜好设置</h2>
      <div class="preferences-content">
        <div class="preference-item">
          <label>喜好音乐类型：</label>
          <div class="multi-select">
            <div v-for="genre in availableGenres" 
                 :key="genre" 
                 :class="{ selected: selectedGenres.includes(genre) }"
                 @click="toggleGenre(genre)" 
                 class="select-item">
              {{ genre }}
            </div>
          </div>
        </div>
        <div class="preference-item">
          <label>喜好歌手：</label>
          <div class="multi-select">
            <div v-for="artist in availableArtists" 
                 :key="artist"
                 :class="{ selected: selectedArtists.includes(artist) }" 
                 @click="toggleArtist(artist)" 
                 class="select-item">
              {{ artist }}
            </div>
          </div>
        </div>
        <div class="preference-item">
          <label>常听时段：</label>
          <div class="multi-select">
            <div v-for="time in listeningTimes" 
                 :key="time" 
                 :class="{ selected: selectedTimes.includes(time) }"
                 @click="toggleTime(time)" 
                 class="select-item">
              {{ time }}
            </div>
          </div>
        </div>
        <button class="btn-save-preferences" @click="savePreferences">
          保存设置
        </button>
      </div>
    </div>

    <!-- 个人音乐统计卡片 -->
    <div class="card statistics">
      <h2>个人音乐统计</h2>
      <div class="stats-content">
        <div class="stats-section">
          <h3>最常听的音乐类型</h3>
          <div class="stats-list">
            <div v-for="(stat, index) in musicStats.genre_stats" 
                 :key="index" 
                 class="stat-item">
              <span class="stat-name">{{ stat.genre }}</span>
              <span class="stat-count">{{ stat.count }}次</span>
            </div>
            <div v-if="musicStats.genre_stats.length === 0" class="no-data">
              暂无数据
            </div>
          </div>
        </div>
        <div class="stats-section">
          <h3>最常听歌手</h3>
          <div class="stats-list">
            <div v-for="(stat, index) in musicStats.artist_stats" 
                 :key="index" 
                 class="stat-item">
              <span class="stat-name">{{ stat.artist }}</span>
              <span class="stat-count">{{ stat.count }}次</span>
            </div>
            <div v-if="musicStats.artist_stats.length === 0" class="no-data">
              暂无数据
            </div>
          </div>
        </div>
        <div class="stats-section">
          <h3>听歌总数</h3>
          <div class="total-plays">
            {{ musicStats.total_plays }}首
          </div>
        </div>
        <div class="stats-section">
          <h3>最近播放</h3>
          <div class="recent-plays">
            <div v-for="(play, index) in recentPlays" 
                 :key="index" 
                 class="recent-play-item">
              <span class="song-title">{{ play.title }}</span>
              <span class="song-artist">{{ play.artist }}</span>
              <span class="play-time">{{ formatTime(play.played_at) }}</span>
            </div>
            <div v-if="recentPlays.length === 0" class="no-data">
              暂无播放记录
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showChangePassword" class="modal">
      <div class="modal-content">
        <h3>修改密码</h3>
        <div class="input-group">
          <label>原密码：</label>
          <input type="password" v-model="oldPassword" />
        </div>
        <div class="input-group">
          <label>新密码：</label>
          <input type="password" v-model="newPassword" />
        </div>
        <div class="input-group">
          <label>确认新密码：</label>
          <input type="password" v-model="confirmPassword" />
        </div>
        <div class="modal-buttons">
          <button @click="changePassword">确认</button>
          <button @click="showChangePassword = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const user = ref(JSON.parse(sessionStorage.getItem('user')));
    const isEditingUsername = ref(false);
    const newUsername = ref('');
    const showChangePassword = ref(false);
    const oldPassword = ref('');
    const newPassword = ref('');
    const confirmPassword = ref('');

    // 音乐喜好设置数据
    const selectedGenres = ref([]);
    const selectedArtists = ref([]);
    const selectedTimes = ref([]);
    
    // 统计数据
    const musicStats = ref({
      genre_stats: [],
      artist_stats: [],
      total_plays: 0
    });
    const recentPlays = ref([]);

    // 可选项数据
    const availableGenres = ref(['流行', '摇滚', '民谣', '电子', '古典', '爵士', '说唱']);
    const availableArtists = ref(['周杰伦', '林俊杰', '陈奕迅', '张学友', '王菲', '邓紫棋', '五月天']);
    const listeningTimes = ref(['早晨', '中午', '下午', '晚上', '深夜']);

    // 加载用户数据
    const loadUserData = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/preferences/preferences?userid=${user.value.userid}`);
        if (response.data.success) {
          selectedGenres.value = response.data.preferences.favorite_genres;
          selectedArtists.value = response.data.preferences.favorite_artists;
          selectedTimes.value = response.data.preferences.listening_times;
        }
      } catch (error) {
        console.error('加载用户数据失败:', error);
      }
    };

    // 加载用户统计数据
    const loadUserStats = async () => {
      try {
        const statsResponse = await axios.get(`http://localhost:5000/user_stats/stats/music?userid=${user.value.userid}`);
        if (statsResponse.data.success) {
          musicStats.value = statsResponse.data.stats;
        }

        const recentResponse = await axios.get(`http://localhost:5000/user_stats/stats/recent?userid=${user.value.userid}`);
        if (recentResponse.data.success) {
          recentPlays.value = recentResponse.data.recent_plays;
        }
      } catch (error) {
        console.error('加载用户统计数据失败:', error);
      }
    };

    // 用户名编辑方法
    const startEditUsername = () => {
      newUsername.value = user.value.username;
      isEditingUsername.value = true;
    };

    const cancelEditUsername = () => {
      isEditingUsername.value = false;
      newUsername.value = '';
    };

    const saveUsername = async () => {
      try {
        const response = await axios.post('http://localhost:5000/auth/change-username', {
          userid: user.value.userid,
          new_username: newUsername.value
        });

        if (response.data.success) {
          const updatedUser = response.data.user;
          sessionStorage.setItem('user', JSON.stringify(updatedUser));
          user.value = updatedUser;
          isEditingUsername.value = false;
          alert('用户名修改成功！');
        } else {
          alert(response.data.message);
        }
      } catch (error) {
        console.error('修改用户名失败:', error);
        alert('修改失败，请稍后重试');
      }
    };

    // 密码修改方法
    const changePassword = async () => {
      if (newPassword.value !== confirmPassword.value) {
        alert('两次输入的新密码不一致');
        return;
      }

      if (newPassword.value.length < 6) {
        alert('新密码长度不能少于6位');
        return;
      }

      try {
        const response = await axios.post('http://localhost:5000/auth/change-password', {
          userid: user.value.userid,
          old_password: oldPassword.value,
          new_password: newPassword.value
        });

        if (response.data.success) {
          alert('密码修改成功！');
          showChangePassword.value = false;
          oldPassword.value = '';
          newPassword.value = '';
          confirmPassword.value = '';
        } else {
          alert(response.data.message);
        }
      } catch (error) {
        console.error('修改密码失败:', error);
        alert('修改失败，请稍后重试');
      }
    };

    // 喜好设置方法
    const toggleGenre = (genre) => {
      const index = selectedGenres.value.indexOf(genre);
      if (index === -1) {
        selectedGenres.value.push(genre);
      } else {
        selectedGenres.value.splice(index, 1);
      }
    };

    const toggleArtist = (artist) => {
      const index = selectedArtists.value.indexOf(artist);
      if (index === -1) {
        selectedArtists.value.push(artist);
      } else {
        selectedArtists.value.splice(index, 1);
      }
    };

    const toggleTime = (time) => {
      const index = selectedTimes.value.indexOf(time);
      if (index === -1) {
        selectedTimes.value.push(time);
      } else {
        selectedTimes.value.splice(index, 1);
      }
    };

    const savePreferences = async () => {
      try {
        const response = await axios.post('http://localhost:5000/preferences/preferences', {
          userid: user.value.userid,
          favorite_genres: selectedGenres.value,
          favorite_artists: selectedArtists.value,
          listening_times: selectedTimes.value
        });

        if (response.data.success) {
          alert('偏好设置保存成功！');
        } else {
          alert(response.data.message);
        }
      } catch (error) {
        console.error('保存偏好设置失败:', error);
        alert('保存失败，请稍后重试');
      }
    };

    // 格式化时间
    const formatTime = (isoString) => {
      const date = new Date(isoString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    // 组件挂载时加载数据
    onMounted(() => {
      loadUserData();
      loadUserStats();
    });

    return {
      user,
      isEditingUsername,
      newUsername,
      showChangePassword,
      oldPassword,
      newPassword,
      confirmPassword,
      selectedGenres,
      selectedArtists,
      selectedTimes,
      availableGenres,
      availableArtists,
      listeningTimes,
      musicStats,
      recentPlays,
      startEditUsername,
      cancelEditUsername,
      saveUsername,
      changePassword,
      toggleGenre,
      toggleArtist,
      toggleTime,
      savePreferences,
      formatTime
    };
  }
};
</script>

<style scoped>
.my-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  padding: 20px;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.user-identity {
  padding: 4px 8px;
  border-radius: 4px;
  background: #e8f0fe;
  color: #4f81e4;
}

.user-identity.admin {
  background: #fef0e8;
  color: #e4814f;
}

.info-item {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.info-item label {
  width: 80px;
  color: #666;
}

.username-display {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-edit, .btn-save, .btn-cancel {
  padding: 4px 8px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.btn-edit {
  background: #e8f0fe;
  color: #4f81e4;
}

.btn-save {
  background: #4f81e4;
  color: white;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.preferences-content {
  padding: 15px;
}

.preference-item {
  margin-bottom: 20px;
}

.preference-item label {
  display: block;
  margin-bottom: 10px;
  color: #666;
}

.multi-select {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.select-item {
  padding: 6px 12px;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s;
}

.select-item.selected {
  background: #4f81e4;
  color: white;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.recent-play-item {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 10px;
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
}

.input-group {
  margin-bottom: 15px;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
}

.input-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.modal-buttons button {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.modal-buttons button:first-child {
  background: #4f81e4;
  color: white;
}

.modal-buttons button:last-child {
  background: #f44336;
  color: white;
}

.btn-save-preferences {
  width: 100%;
  padding: 10px;
  background: #4f81e4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 20px;
}

.btn-save-preferences:hover {
  background: #2a61c5;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 10px;
  font-style: italic;
}
</style>