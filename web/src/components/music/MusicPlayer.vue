<template>
    <div class="music-player" v-if="currentTrack">
        <audio 
            ref="audio" 
            :src="currentTrack.url" 
            @ended="playNext" 
            @timeupdate="updateProgress"
            @play="onPlay"
        ></audio>

        <div class="player-info">
            <div class="track-info">
                <h3>{{ currentTrack.title }}</h3>
                <p>{{ currentTrack.artist_name }}</p>
            </div>

            <div class="progress-bar">
                <div class="progress" :style="{ width: progress + '%' }"></div>
            </div>

            <div class="player-controls">
                <button @click="togglePlay" class="control-btn">
                    {{ isPlaying ? '暂停' : '播放' }}
                </button>
                <button @click="stop" class="control-btn">停止</button>
                <button @click="fastForward" class="control-btn">快进</button>
                <button @click="playNext" class="control-btn">下一首</button>
                <button @click="toggleQueuePanel" class="control-btn">
                    播放队列
                </button>
            </div>
        </div>

        <!-- 播放队列面板 -->
        <div class="queue-panel" v-if="showQueuePanel">
            <div class="queue-header">
                <h3>播放队列</h3>
                <button @click="clearQueue" class="clear-btn">清空队列</button>
            </div>
            <div class="queue-list">
                <div v-for="(track, index) in playQueue" 
                     :key="track.id"
                     :class="['queue-item', { active: currentTrack.id === track.id }]">
                    <span class="track-name">{{ track.title }} - {{ track.artist_name }}</span>
                    <div class="queue-item-controls">
                        <button @click="playTrack(track)" class="queue-btn">播放</button>
                        <button @click="removeFromQueue(index)" class="queue-btn remove">删除</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { emitter } from '../../eventBus';
import axios from 'axios';

export default {
    data() {
        return {
            isPlaying: false,
            currentTrack: null,
            playQueue: [],
            progress: 0,
            userId: null,
            showQueuePanel: false
        }
    },
    mounted() {
        // 获取用户信息
        const userInfo = sessionStorage.getItem('user');
        if (userInfo) {
            this.userId = JSON.parse(userInfo).userid;
            this.loadPlayQueue();
        }

        // 监听添加到队列事件
        emitter.on('add-to-queue', (track) => {
            this.addToQueue(track);
        });

        // 监听播放音乐事件
        emitter.on('play-music', (track) => {
            this.playTrack(track);
        });
    },
    methods: {
        async recordPlay() {
            if (!this.userId || !this.currentTrack) return;

            try {
                const response = await axios.post(`http://localhost:5000/music/${this.currentTrack.id}/play`, {
                    userid: this.userId
                });
                
                if (response.data.success) {
                    console.log('播放记录已添加，播放次数已更新');
                }
            } catch (error) {
                console.error('记录播放失败:', error);
            }
        },

        async onPlay() {
            await this.recordPlay();
        },

        loadPlayQueue() {
            const queue = localStorage.getItem(`playQueue_${this.userId}`);
            this.playQueue = queue ? JSON.parse(queue) : [];
            if (this.playQueue.length > 0 && !this.currentTrack) {
                this.currentTrack = this.playQueue[0];
            }
        },

        savePlayQueue() {
            localStorage.setItem(`playQueue_${this.userId}`, JSON.stringify(this.playQueue));
        },

        toggleQueuePanel() {
            this.showQueuePanel = !this.showQueuePanel;
        },

        removeFromQueue(index) {
            if (this.playQueue[index].id === this.currentTrack.id) {
                if (this.playQueue.length > 1) {
                    const nextIndex = (index + 1) % this.playQueue.length;
                    this.currentTrack = this.playQueue[nextIndex];
                } else {
                    this.stop();
                    this.currentTrack = null;
                }
            }
            
            this.playQueue.splice(index, 1);
            this.savePlayQueue();
        },

        clearQueue() {
            if (confirm('确定要清空播放队列吗？')) {
                this.stop();
                this.progress = 0;
                this.playQueue = [];
                this.currentTrack = null;
                this.savePlayQueue();
                this.showQueuePanel = false;
            }
        },

        addToQueue(track) {
            if (!this.userId) return;
            
// 检查歌曲是否已经在队列中
const isInQueue = this.playQueue.some(t => t.id === track.id);

if (!isInQueue) {
                this.playQueue.push(track);
                this.savePlayQueue();
                // 如果当前没有正在播放的歌曲，直接播放这首
                if (!this.currentTrack) {
                    this.currentTrack = track;
                    this.$nextTick(() => {
                        const audio = this.$refs.audio;
                        audio.play();
                        this.isPlaying = true;
                    });
                }
            } else {
                // 可以选择是否提示用户（可选）
                console.log('该歌曲已在播放队列中');
            }
        },

        async playTrack(track) {
            if (!this.userId) return;

            this.currentTrack = track;

            if (!this.playQueue.some(t => t.id === track.id)) {
                this.addToQueue(track);
            }

            this.$nextTick(async () => {
                const audio = this.$refs.audio;
                await audio.play();
                this.isPlaying = true;
            });
        },

        async togglePlay() {
            if (!this.userId) return;

            const audio = this.$refs.audio;
            if (this.isPlaying) {
                audio.pause();
                this.isPlaying = false;
            } else {
                await audio.play();
                this.isPlaying = true;
            }
        },

        stop() {
            if (!this.userId) return;

            const audio = this.$refs.audio;
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }
            this.isPlaying = false;
            this.progress = 0;
        },

        fastForward() {
            if (!this.userId) return;

            const audio = this.$refs.audio;
            audio.currentTime += 10;
        },

        async playNext() {
            if (!this.userId || this.playQueue.length <= 1) return;

            const currentIndex = this.playQueue.findIndex(t => t.id === this.currentTrack.id);
            const nextIndex = (currentIndex + 1) % this.playQueue.length;
            this.currentTrack = this.playQueue[nextIndex];

            this.$nextTick(async () => {
                const audio = this.$refs.audio;
                await audio.play();
                this.isPlaying = true;
            });
        },

        updateProgress() {
            const audio = this.$refs.audio;
            if (audio && !isNaN(audio.duration)) {
                this.progress = (audio.currentTime / audio.duration) * 100;
            }
        }
    }
}
</script>

<style scoped>
.music-player {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #333;
    color: white;
    padding: 15px;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.player-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.track-info {
    text-align: center;
}

.track-info h3 {
    margin: 0;
    font-size: 1.1em;
}

.track-info p {
    margin: 5px 0;
    font-size: 0.9em;
    color: #ccc;
}

.progress-bar {
    width: 100%;
    height: 4px;
    background-color: #555;
    border-radius: 2px;
    overflow: hidden;
}

.progress {
    height: 100%;
    background-color: #1db954;
    transition: width 0.1s linear;
}

.player-controls {
    display: flex;
    gap: 10px;
    justify-content: center;
}

.queue-panel {
    position: fixed;
    bottom: 100px;
    right: 20px;
    width: 300px;
    max-height: 400px;
    background-color: #333;
    border-radius: 8px;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
    padding: 15px;
    overflow-y: auto;
}

.queue-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.queue-header h3 {
    margin: 0;
    color: white;
}

.clear-btn {
    padding: 5px 10px;
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.queue-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.queue-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: #444;
    border-radius: 4px;
    color: white;
}

.queue-item.active {
    background-color: #1db954;
}

.track-name {
    flex: 1;
    margin-right: 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.queue-item-controls {
    display: flex;
    gap: 5px;
}

.queue-btn {
    padding: 4px 8px;
    background-color: #555;
    border: none;
    border-radius: 3px;
    color: white;
    cursor: pointer;
    font-size: 0.9em;
}

.queue-btn.remove {
    background-color: #dc3545;
}

.queue-btn:hover {
    opacity: 0.9;
}

.control-btn {
    padding: 8px 15px;
    background-color: #444;
    border: none;
    border-radius: 4px;
    color: white;
    cursor: pointer;
    transition: background-color 0.2s;
}

.control-btn:hover {
    background-color: #555;
}
</style>