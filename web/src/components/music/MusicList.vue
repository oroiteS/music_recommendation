<template>
    <div class="music-list">
        <div class="header">
            <h2>音乐列表</h2>
            <!-- 管理员导入音乐按钮 -->
            <button v-if="isAdmin" @click="showImportDialog" class="import-btn">
                导入音乐
            </button>
        </div>

        <!-- 导入音乐弹窗 -->
        <div v-if="showDialog" class="dialog-overlay">
            <div class="dialog">
                <h3>导入音乐</h3>
                <form @submit.prevent="handleImport">
                    <div class="form-group">
                        <label>歌曲名称*</label>
                        <input v-model="newMusic.title" required>
                    </div>
                    <div class="form-group">
                        <label>歌手名称*</label>
                        <input v-model="newMusic.artist_name" required>
                    </div>
                    <div class="form-group">
                        <label>歌曲风格</label>
                        <input v-model="newMusic.genre">
                    </div>
                    <div class="form-group">
                        <label>封面图片</label>
                        <input type="file" @change="handleCoverUpload" accept="image/*">
                    </div>
                    <div class="form-group">
                        <label>音乐文件*</label>
                        <input type="file" @change="handleMusicUpload" accept="audio/*" required>
                    </div>
                    <div class="dialog-buttons">
                        <button type="submit">确认</button>
                        <button type="button" @click="showDialog = false">取消</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 现有的音乐列表展示 -->
        <div class="music-grid">
            <div v-for="music in musicList" :key="music.id" class="music-card" @click="goToMusicDetail(music.id)">
                <img :src="music.cover_url" :alt="music.title" class="music-cover">
                <div class="music-info">
                    <h3>{{ music.title }}</h3>
                    <p>{{ music.artist_name }}</p>
                    <p>{{ music.genre }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            musicList: [],
            showDialog: false,
            newMusic: {
                title: '',
                artist_name: '',
                genre: '',
                cover_url: ''
            },
            musicFile: null,
            isAdmin: false
        }
    },
    async created() {
         // 检查用户是否为管理员
         const user = JSON.parse(sessionStorage.getItem('user') || '{}');
        this.isAdmin = user.user_identity === 1;

        // 获取音乐列表
        try {
            const response = await axios.get('http://localhost:5000/music/list');
            if (response.data.success) {
                this.musicList = response.data.data;
            }
        } catch (error) {
            console.error('获取音乐列表失败:', error);
        }
    },
    methods: {
        showImportDialog() {
            this.showDialog = true;
        },
        handleCoverUpload(event) {
            const file = event.target.files[0];
            if (file) {
                // 处理封面上传
                const formData = new FormData();
                formData.append('file', file);
                formData.append('artist_name', this.newMusic.artist_name);
                formData.append('title', this.newMusic.title);

                axios.post('http://localhost:5000/music/upload-cover', formData)
                    .then(response => {
                        if (response.data.success) {
                            this.newMusic.cover_url = response.data.url;
                        }
                    })
                    .catch(error => console.error('封面上传失败:', error));
            }
        },
        handleMusicUpload(event) {
            this.musicFile = event.target.files[0];
        },
        async handleImport() {
            if (!this.musicFile) {
                alert('请选择音乐文件');
                return;
            }

            try {
                // 上传音乐文件 
                const formData = new FormData();
                formData.append('file', this.musicFile);
                formData.append('title', this.newMusic.title);
                formData.append('artist_name', this.newMusic.artist_name);

                const response = await axios.post('http://localhost:5000/music/upload', formData);
                
                if (response.data.success) {
                    // 创建音乐记录
                    await axios.post('http://localhost:5000/music/create', {
                        ...this.newMusic,
                        file_path: response.data.file_path
                    });

                    // 刷新音乐列表
                    const listResponse = await axios.get('http://localhost:5000/music/list');
                    if (listResponse.data.success) {
                        this.musicList = listResponse.data.data;
                    }

                    this.showDialog = false;
                    this.newMusic = {
                        title: '',
                        artist_name: '',
                        genre: '',
                        cover_url: ''
                    };
                    this.musicFile = null;
                }
            } catch (error) {
                console.error('导入音乐失败:', error);
                alert('导入音乐失败');
            }
        },
        goToMusicDetail(musicId) {
            this.$router.push(`/music/${musicId}`);
        }
    }
}
</script>

<style scoped>
.music-list {
    padding: 20px;
}

.music-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    padding: 20px;
}

.music-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.2s;
    cursor: pointer;
}

.music-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.music-cover {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.music-info {
    padding: 10px;
}

.music-info h3 {
    margin: 0;
    font-size: 1.1em;
}

.music-info p {
    margin: 5px 0;
    color: #666;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
}

.import-btn {
    padding: 8px 16px;
    background-color: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.dialog-overlay {
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

.dialog {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 400px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
}

.form-group input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.dialog-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.dialog-buttons button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.dialog-buttons button[type="submit"] {
    background-color: #42b983;
    color: white;
}

.dialog-buttons button[type="button"] {
    background-color: #666;
    color: white;
}
</style>