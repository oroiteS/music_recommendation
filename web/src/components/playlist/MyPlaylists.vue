<template>
    <div class="playlists-container">
        <div class="playlists-header">
            <h2>我的歌单</h2>
            <button @click="showCreateDialog = true" class="create-btn">创建歌单</button>
        </div>

        <!-- 歌单列表 -->
        <div class="playlists-grid">
            <div v-for="playlist in playlists" :key="playlist.id" class="playlist-card">
                <div class="playlist-info" @click="goToPlaylist(playlist.id)">
                    <h3>{{ playlist.title }}</h3>
                    <p class="description">{{ playlist.description || '暂无描述' }}</p>
                    <p class="created-at">创建时间：{{ playlist.created_at }}</p>
                </div>
                <button @click="deletePlaylist(playlist.id)" class="delete-btn">删除歌单</button>
            </div>
        </div>

        <!-- 创建歌单对话框 -->
        <div v-if="showCreateDialog" class="dialog-overlay">
            <div class="dialog">
                <h3>创建新歌单</h3>
                <input v-model="newPlaylist.title" type="text" placeholder="歌单名称" class="input-field">
                <textarea v-model="newPlaylist.description" placeholder="歌单描述（可选）" class="input-field"></textarea>
                <div class="dialog-buttons">
                    <button @click="createPlaylist" class="confirm-btn">创建</button>
                    <button @click="showCreateDialog = false" class="cancel-btn">取消</button>
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
            playlists: [],
            showCreateDialog: false,
            newPlaylist: {
                title: '',
                description: ''
            },
            userId: null
        }
    },
    mounted() {
        const userInfo = sessionStorage.getItem('user');
        if (userInfo) {
            this.userId = JSON.parse(userInfo).userid;
            this.loadPlaylists();
        } else {
            this.$router.push('/login');
        }
    },
    methods: {
        async loadPlaylists() {
            try {
                const response = await axios.get(`http://localhost:5000/playlist/user/${this.userId}`);
                if (response.data.success) {
                    this.playlists = response.data.data;
                }
            } catch (error) {
                console.error('加载歌单失败:', error);
            }
        },

        async createPlaylist() {
            if (!this.newPlaylist.title.trim()) {
                alert('请输入歌单名称');
                return;
            }

            try {
                const response = await axios.post('http://localhost:5000/playlist/', {
                    userid: this.userId,
                    title: this.newPlaylist.title,
                    description: this.newPlaylist.description
                });

                if (response.data.success) {
                    this.playlists.push(response.data.data);
                    this.showCreateDialog = false;
                    this.newPlaylist = { title: '', description: '' };
                }else{
                    console.log(response.data)
                }
            } catch (error) {
                console.error('创建歌单失败:', error);
            }
        },

        async deletePlaylist(playlistId) {
            if (!confirm('确定要删除这个歌单吗？')) return;

            try {
                const response = await axios.delete(`http://localhost:5000/playlist/${playlistId}`);
                if (response.data.success) {
                    this.playlists = this.playlists.filter(p => p.id !== playlistId);
                }
            } catch (error) {
                console.error('删除歌单失败:', error);
            }
        },

        goToPlaylist(playlistId) {
            this.$router.push(`/playlist/${playlistId}`);
        }
    }
}
</script>

<style scoped>
.playlists-container {
    padding: 20px;
}

.playlists-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.create-btn {
    padding: 10px 20px;
    background-color: #1db954;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.playlists-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.playlist-card {
    background-color: #fff;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.playlist-info {
    cursor: pointer;
}

.playlist-info h3 {
    margin: 0 0 10px 0;
    color: #333;
}

.description {
    color: #666;
    margin: 10px 0;
}

.created-at {
    color: #999;
    font-size: 0.9em;
}

.delete-btn {
    margin-top: 10px;
    padding: 5px 10px;
    background-color: #dc3545;
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
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}

.dialog {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    width: 400px;
}

.input-field {
    width: 100%;
    margin: 10px 0;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

textarea.input-field {
    height: 100px;
    resize: vertical;
}

.dialog-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.confirm-btn,
.cancel-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.confirm-btn {
    background-color: #1db954;
    color: white;
}

.cancel-btn {
    background-color: #6c757d;
    color: white;
}
</style>