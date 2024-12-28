<template>
    <div class="music-detail" v-if="music">
        <div class="music-header">
            <img :src="music.cover_url" :alt="music.title" class="music-cover">
            <div class="music-info">
                <h1>{{ music.title }}</h1>
                <p class="artist">歌手：{{ music.artist_name }}</p>
                <p class="genre">流派：{{ music.genre }}</p>
                <p class="play-count">播放次数：{{ music.play_count }}</p>

                <button v-if="isAdmin" @click="goToEdit" class="edit-btn">
                    编辑音乐信息
                </button>

                <div class="rating-section">
                    <div class="average-rating">
                        <span>平均评分：{{ averageRating.toFixed(1) }}</span>
                        <span class="rating-count">({{ ratingCount }}人评分)</span>
                    </div>
                    <div class="user-rating">
                        <span>我的评分：</span>
                        <div class="stars">
                            <span v-for="n in 5" :key="n" class="star"
                                :class="{ 'active': n <= userRating, 'hover': n <= hoverRating }"
                                @click="submitRating(n)" @mouseover="hoverRating = n"
                                @mouseleave="hoverRating = 0">★</span>
                        </div>
                    </div>
                </div>

                <div class="action-buttons">
                    <button @click="playMusic" class="play-btn">播放</button>
                    <button @click="showCollectDialog = true" class="playlist-btn">收藏到歌单</button>
                    <button @click="addToQueue" class="queue-btn">加入播放队列</button>
                </div>
            </div>
        </div>

        <!-- 收藏对话框 -->
        <div v-if="showCollectDialog" class="dialog-overlay">
            <div class="dialog">
                <h3>收藏到歌单</h3>

                <!-- 创建新歌单部分 -->
                <div class="new-playlist-section">
                    <button @click="showNewPlaylistForm = !showNewPlaylistForm" class="create-btn">
                        {{ showNewPlaylistForm ? '取消创建' : '创建新歌单' }}
                    </button>

                    <div v-if="showNewPlaylistForm" class="new-playlist-form">
                        <input v-model="newPlaylist.title" type="text" placeholder="歌单名称" class="input-field">
                        <textarea v-model="newPlaylist.description" placeholder="歌单描述（可选）"
                            class="input-field"></textarea>
                        <button @click="createAndAddToPlaylist" class="confirm-btn">
                            创建并添加
                        </button>
                    </div>
                </div>

                <!-- 现有歌单列表 -->
                <div class="playlists-list">
                    <h4>选择现有歌单</h4>
                    <div v-for="playlist in userPlaylists" :key="playlist.id" class="playlist-item"
                        @click="addToPlaylist(playlist.id)">
                        <span class="playlist-title">{{ playlist.title }}</span>
                        <span class="playlist-desc">{{ playlist.description || '暂无描述' }}</span>
                    </div>
                </div>

                <button @click="showCollectDialog = false" class="close-btn">关闭</button>
            </div>
        </div>

        <!-- 评论区 -->
        <div class="comments-section">
            <h2>评论区</h2>
            <div class="comment-input">
                <textarea v-model="newComment" placeholder="写下你的评论..."></textarea>
                <button @click="submitComment">发表评论</button>
            </div>
            <div class="comments-list">
                <div v-for="comment in comments" :key="comment.id" class="comment-item">
                    <div class="comment-header">
                        <span class="username">{{ comment.username }}</span>
                        <span class="time">{{ comment.created_at }}</span>
                    </div>
                    <p class="comment-content">{{ comment.comment_text }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { emitter } from '../../eventBus'; // 确保引入的是 emitter

export default {
    data() {
        return {
            music: null,
            comments: [],
            newComment: '',
            userRating: 0,
            hoverRating: 0,
            averageRating: 0,
            ratingCount: 0,
            showCollectDialog: false,
            showNewPlaylistForm: false,
            userPlaylists: [],
            newPlaylist: {
                title: '',
                description: ''
            },
            userId: null,
            isAdmin: false
        }
    },
    async created() {
        const userInfo = sessionStorage.getItem('user');
        if (userInfo) { 
            this.userId = JSON.parse(userInfo).userid;
        }
        const musicId = this.$route.params.id;
        await this.fetchMusicDetails(musicId);
        await this.fetchComments(musicId);
        await this.fetchRatings(musicId);
        await this.loadUserPlaylists();
        if (sessionStorage.getItem('user')) {
            const user = JSON.parse(sessionStorage.getItem('user'));
            this.isAdmin = (user.user_identity === 1);
        }
    },
    methods: {
        async loadUserPlaylists() {
            if (!this.userId) return;

            try {
                const response = await axios.get(`http://localhost:5000/playlist/user/${this.userId}`);
                if (response.data.success) {
                    this.userPlaylists = response.data.data;
                }
            } catch (error) {
                console.error('加载歌单失败:', error);
            }
        },

        async createAndAddToPlaylist() {
            if (!this.newPlaylist.title.trim()) {
                alert('请输入歌单名称');
                return;
            }

            try {
                // 创建新歌单
                const createResponse = await axios.post('http://localhost:5000/playlist/', {
                    userid: this.userId,
                    title: this.newPlaylist.title,
                    description: this.newPlaylist.description
                });

                if (createResponse.data.success) {
                    // 添加歌曲到新歌单
                    await this.addToPlaylist(createResponse.data.data.id);
                    this.showNewPlaylistForm = false;
                    this.newPlaylist = { title: '', description: '' };
                    await this.loadUserPlaylists();
                }
            } catch (error) {
                console.error('创建歌单失败:', error);
            }
        },

        async addToPlaylist(playlistId) {
            try {
                const response = await axios.post(`http://localhost:5000/playlist/${playlistId}/songs`, {
                    music_id: this.music.id
                });

                if (response.data.success) {
                    alert('收藏成功！');
                    this.showCollectDialog = false;
                } else {
                    alert(response.data.message);
                }
            } catch (error) {
                console.error('收藏失败:', error);
                alert('收藏失败，请重试');
            }
        },
        async fetchMusicDetails(musicId) {
            try {
                const response = await axios.get(`http://localhost:5000/music/${musicId}`);
                if (response.data.success) {
                    this.music = response.data.data;
                }
            } catch (error) {
                console.error('获取音乐详情失败:', error);
            }
        },
        async fetchComments(musicId) {
            try {
                const response = await axios.get(`http://localhost:5000/music/${musicId}/comments`);
                if (response.data.success) {
                    this.comments = response.data.data;
                }
            } catch (error) {
                console.error('获取评论失败:', error);
            }
        },
        async submitComment() {
            if (!this.newComment.trim()) return;

            const user = JSON.parse(sessionStorage.getItem('user'));
            if (!user) {
                alert('请先登录');
                return;
            }

            try {
                const response = await axios.post(`http://localhost:5000/music/${this.music.id}/comments`, {
                    comment_text: this.newComment,
                    userid: user.userid
                });
                if (response.data.success) {
                    this.comments.unshift(response.data.data);
                    this.newComment = '';
                }
            } catch (error) {
                console.error('发表评论失败:', error);
            }
        },
        async fetchRatings(musicId) {
            try {
                const response = await axios.get(`http://localhost:5000/music/${musicId}/ratings`);
                if (response.data.success) {
                    this.averageRating = response.data.data.average_rating;
                    this.ratingCount = response.data.data.rating_count;
                    this.userRating = response.data.data.user_rating || 0;
                }
            } catch (error) {
                console.error('获取评分失败:', error);
            }
        },
        async submitRating(rating) {
            const user = JSON.parse(sessionStorage.getItem('user'));
            if (!user) {
                alert('请先登录');
                return;
            }

            try {
                const response = await axios.post(`http://localhost:5000/music/${this.music.id}/ratings`, {
                    rating_value: rating,
                    userid: user.userid
                });
                if (response.data.success) {
                    this.userRating = rating;
                    this.averageRating = response.data.data.new_average;
                    this.ratingCount = response.data.data.new_count;
                }
            } catch (error) {
                console.error('提交评分失败:', error);
            }
        },
        async toggleLike() {
            this.isLiked = !this.isLiked;
        },
        addToQueue() {
            const track = {
                id: this.music.id,
                title: this.music.title,
                artist_name: this.music.artist_name,
                url: `/static/music/${this.music.artist_name}-${this.music.title}.mp3`,
                cover_url: this.music.cover_url  // 添加封面URL
            };
            emitter.emit('add-to-queue', track);
        },
        playMusic() {
            const track = {
                id: this.music.id,
                title: this.music.title,
                artist_name: this.music.artist_name,
                url: `/static/music/${this.music.artist_name}-${this.music.title}.mp3`
            };
            emitter.emit('play-music', track);
        },
        goToEdit() {
            this.$router.push(`/music/${this.music.id}/edit`);
        }
    }
}
</script>

<style scoped>
.music-detail {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.music-header {
    display: flex;
    gap: 30px;
    margin-bottom: 40px;
}

.music-cover {
    width: 300px;
    height: 300px;
    object-fit: cover;
    border-radius: 8px;
}

.music-info {
    flex: 1;
}

.action-buttons {
    margin-top: 20px;
    display: flex;
    gap: 10px;
}

.action-buttons button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
}

.play-btn {
    background-color: #1db954;
    color: white;
}

.playlist-btn {
    background-color: #535353;
    color: white;
}

.like-btn {
    background-color: white;
    border: 1px solid #1db954 !important;
    color: #1db954;
}

.like-btn.liked {
    background-color: #1db954;
    color: white;
}

.comments-section {
    margin-top: 40px;
    margin-bottom: 20px;
    /* 确保评论区底部有足够空间 */
}

.comment-input {
    margin-bottom: 20px;
}

.comment-input textarea {
    width: 100%;
    height: 100px;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    resize: vertical;
}

.comment-item {
    padding: 15px;
    border-bottom: 1px solid #eee;
}

.comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.username {
    font-weight: bold;
}

.time {
    color: #888;
    font-size: 0.9em;
}

.rating-section {
    margin: 20px 0;
}

.average-rating {
    margin-bottom: 10px;
    font-size: 1.1em;
}

.rating-count {
    color: #666;
    font-size: 0.9em;
    margin-left: 8px;
}

.user-rating {
    display: flex;
    align-items: center;
    gap: 10px;
}

.stars {
    display: flex;
    gap: 5px;
}

.star {
    cursor: pointer;
    font-size: 24px;
    color: #ddd;
}

.star.active {
    color: #ffd700;
}

.star.hover {
    color: #ffed4a;
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
    z-index: 1000;
}

.dialog {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    width: 500px;
    max-height: 80vh;
    overflow-y: auto;
}

.new-playlist-section {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.create-btn {
    padding: 8px 16px;
    background-color: #1db954;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 10px;
}

.new-playlist-form {
    margin-top: 15px;
}

.input-field {
    width: 100%;
    margin-bottom: 10px;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

textarea.input-field {
    height: 80px;
    resize: vertical;
}

.playlists-list {
    max-height: 300px;
    overflow-y: auto;
}

.playlist-item {
    padding: 10px;
    border: 1px solid #eee;
    border-radius: 4px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.playlist-item:hover {
    background-color: #f5f5f5;
}

.playlist-title {
    display: block;
    font-weight: bold;
    margin-bottom: 4px;
}

.playlist-desc {
    display: block;
    font-size: 0.9em;
    color: #666;
}

.close-btn {
    margin-top: 15px;
    padding: 8px 16px;
    background-color: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.confirm-btn {
    padding: 8px 16px;
    background-color: #1db954;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    width: 100%;
}

.edit-btn {
    padding: 8px 16px;
    background-color: #f0ad4e;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 10px;
}

.edit-btn:hover {
    background-color: #ec971f;
}
</style>