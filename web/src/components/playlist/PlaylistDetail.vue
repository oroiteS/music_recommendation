<template>
    <!-- 添加加载状态显示 -->
    <div v-if="loading" class="loading">
        加载中...
    </div>

    <!-- 添加错误状态显示 -->
    <div v-else-if="error" class="error">
        {{ error }}
    </div>
    <div class="playlist-detail" v-if="playlist">
        <div class="playlist-header">
            <h2>{{ playlist.title }}</h2>
            <p class="description">{{ playlist.description || '暂无描述' }}</p>
            <p class="created-at">创建时间：{{ playlist.created_at }}</p>
        </div>

        <div class="songs-list">
            <div v-for="song in playlist.songs" :key="song.id" class="song-item">
                <img :src="song.cover_url" :alt="song.title" class="song-cover">
                <div class="song-info">
                    <h3>{{ song.title }}</h3>
                    <p>{{ song.artist_name }}</p>
                </div>
                <div class="song-actions">
                    <button @click="playMusic(song)" class="action-btn">播放</button>
                    <button @click="addToQueue(song)" class="action-btn">添加到播放队列</button>
                    <button @click="removeSong(song.id)" class="action-btn remove">删除</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { emitter } from '../../eventBus';

export default {
    data() {
        return {
            playlist: null,
            userId: null,
            loading: true,
            error: null
        }
    },
    mounted() {
        const userInfo = sessionStorage.getItem('user');
        if (userInfo) {
            this.userId = JSON.parse(userInfo).userid;
            this.loadPlaylist();
        } else {
            this.$router.push('/login');
        }
    },
    methods: {
        async loadPlaylist() {
            this.loading = true;
            this.error = null;
            
            try {
                const playlistId = this.$route.params.id;
                console.log('Loading playlist:', playlistId); // 调试日志
                
                const response = await axios.get(`http://localhost:5000/playlist/${playlistId}`);
                console.log('Playlist response:', response); // 调试日志
                
                if (response.data.success) {
                    this.playlist = response.data.data;
                } else {
                    this.error = response.data.message || '加载歌单失败';
                }
            } catch (error) {
                console.error('加载歌单失败:', error);
                this.error = '加载歌单失败，请稍后重试';
            } finally {
                this.loading = false;
            }
        },

        playMusic(song) {
            const track = {
                id: song.id,
                title: song.title,
                artist_name: song.artist_name,
                url: `/static/music/${song.artist_name}-${song.title}.mp3`
            };
            emitter.emit('play-music', track);
        },

        addToQueue(song) {
            const track = {
                id: song.id,
                title: song.title,
                artist_name: song.artist_name,
                url: `/static/music/${song.artist_name}-${song.title}.mp3`,
                cover_url: song.cover_url  // 添加封面URL
            };
            emitter.emit('add-to-queue', track);
        },

        async removeSong(musicId) {
            if (!confirm('确定要从歌单中删除这首歌吗？')) return;

            try {
                const response = await axios.delete(
                    `http://localhost:5000/playlist/${this.playlist.id}/songs/${musicId}`
                );
                if (response.data.success) {
                    this.playlist.songs = this.playlist.songs.filter(s => s.id !== musicId);
                }
            } catch (error) {
                console.error('删除歌曲失败:', error);
                alert('删除歌曲失败，请重试');
            }
        }   
    }
}
</script>

<style scoped>
.playlist-detail {
    padding: 20px;
}

.playlist-header {
    margin-bottom: 30px;
}

.description {
    color: #666;
    margin: 10px 0;
}

.created-at {
    color: #999;
    font-size: 0.9em;
}

.songs-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.song-item {
    display: flex;
    align-items: center;
    padding: 10px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.song-cover {
    width: 60px;
    height: 60px;
    border-radius: 4px;
    object-fit: cover;
}

.song-info {
    flex: 1;
    margin-left: 15px;
}

.song-info h3 {
    margin: 0;
    color: #333;
}

.song-info p {
    margin: 5px 0 0 0;
    color: #666;
}

.song-actions {
    display: flex;
    gap: 10px;
}

.action-btn {
    padding: 8px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    background-color: #1db954;
    color: white;
}

.action-btn.remove {
    background-color: #dc3545;
}

.loading {
    text-align: center;
    padding: 20px;
    font-size: 1.2em;
    color: #666;
}

.error {
    text-align: center;
    padding: 20px;
    color: #dc3545;
    font-size: 1.2em;
}
</style>