<template>
  <div class="home-page">
    <!-- 推荐歌单部分 -->
    <section class="recommendation-section">
      <h2>为你推荐</h2>
      <div class="playlist-carousel">
        <div class="carousel-arrow left" @click="prevPage">
          <i class="fas fa-chevron-left"></i>
        </div>

        <div class="playlist-grid">
          <transition-group name="carousel" tag="div" class="playlist-items">
            <div v-for="(song, index) in currentPageSongs" :key="song.id" class="playlist-item"
              :style="{ order: index }" @click="playSong(song.id)">
              <div class="song-cover">
                <img :src="song.cover" :alt="song.title">
                <div class="play-icon">
                  <i class="fas fa-play"></i>
                </div>
              </div>
              <div class="song-info">
                <div class="song-title">{{ song.title }}</div>
                <div class="song-artist">{{ song.artist }}</div>
              </div>
            </div>
          </transition-group>
        </div>

        <div class="carousel-arrow right" @click="nextPage">
          <i class="fas fa-chevron-right"></i>
        </div>
      </div>

      <div class="page-indicators">
        <span v-for="n in totalPages" :key="n" :class="['indicator', { active: currentPage === n - 1 }]"
          @click="goToPage(n - 1)">
        </span>
      </div>
    </section>

    <!-- 排行榜部分 -->
    <section class="rankings-section">
      <h2>排行榜</h2>
      <div class="rankings-grid">
        <!-- 歌手排行榜 -->
        <div class="ranking-category">
          <h3>歌手排行榜</h3>
          <div class="ranking-list">
            <div v-for="(artist, index) in rankings.artists" :key="'artist-' + index" class="ranking-item">
              <span class="rank-number">{{ index + 1 }}</span>
              <div class="rank-info">
                <div class="rank-name">{{ artist.name }}</div>
                <div class="rank-detail">热度: {{ artist.popularity }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 热歌排行榜 -->
        <div class="ranking-category">
          <h3>热歌排行榜</h3>
          <div class="ranking-list">
            <div v-for="(song, index) in rankings.hotSongs" :key="'hot-' + index" class="ranking-item"
              @click="playSong(song.id)">
              <span class="rank-number">{{ index + 1 }}</span>
              <div class="rank-info">
                <div class="rank-name">{{ song.title }}</div>
                <div class="rank-detail">{{ song.artist }}</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

export default {
  setup() {
    const router = useRouter();
    const recommendations = ref({
      collaborative: []
    });
    const rankings = ref({
      artists: [],
      hotSongs: [],
      popIndex: []
    });
    const currentPage = ref(0);
    const itemsPerPage = 3;
    const isAnimating = ref(false);

    // 计算总页数
    const totalPages = computed(() => {
      return Math.ceil(recommendations.value.collaborative.length / itemsPerPage);
    });

    // 计算当前页显示的歌曲
    const currentPageSongs = computed(() => {
      const songs = recommendations.value.collaborative;
      const start = currentPage.value * itemsPerPage;
      return songs.slice(start, start + itemsPerPage);
    });

    // 翻页方法
    const nextPage = () => {
      if (isAnimating.value) return;
      isAnimating.value = true;

      setTimeout(() => {
        if (currentPage.value >= totalPages.value - 1) {
          currentPage.value = 0;
        } else {
          currentPage.value++;
        }
        isAnimating.value = false;
      }, 50);
    };

    const prevPage = () => {
      if (isAnimating.value) return;
      isAnimating.value = true;

      setTimeout(() => {
        if (currentPage.value <= 0) {
          currentPage.value = totalPages.value - 1;
        } else {
          currentPage.value--;
        }
        isAnimating.value = false;
      }, 50);
    };

    const goToPage = (page) => {
      if (isAnimating.value) return;
      currentPage.value = page;
    };

    // 加载推荐歌单
    const loadRecommendations = async () => {
      try {
        const user = JSON.parse(sessionStorage.getItem('user'));
        if (!user) return;

        const response = await axios.get('http://localhost:5000/recommendations', {
          params: { userid: user.userid }
        });

        if (response.data.success) {
          recommendations.value = response.data.recommendations;
        }
      } catch (error) {
        console.error('加载推荐歌单失败:', error);
      }
    };

    // 加载排行榜
    const loadRankings = async () => {
      try {
        const response = await axios.get('http://localhost:5000/rankings');
        if (response.data.success) {
          rankings.value = response.data.rankings;
        }
      } catch (error) {
        console.error('加载排行榜失败:', error);
      }
    };

    // 播放歌曲
    const playSong = (songId) => {
      router.push(`/music/${songId}`);
    };

    // 组件挂载时加载数据
    onMounted(() => {
      loadRecommendations();
      loadRankings();
    });

    return {
      recommendations,
      rankings,
      currentPage,
      totalPages,
      currentPageSongs,
      nextPage,
      prevPage,
      goToPage,
      playSong
    };
  }
};
</script>

<style scoped>
.home-page {
  padding: 20px;
}

.recommendation-section,
.rankings-section {
  margin-bottom: 40px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
}

.playlist-carousel {
  position: relative;
  display: flex;
  align-items: center;
  margin: 20px 0;
}

.playlist-grid {
  width: 100%;
  overflow: hidden;
  padding: 0 20px;
}

.playlist-items {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  position: relative;
}

/* 轮播动画 */
.carousel-enter-active,
.carousel-leave-active {
  transition: all 0.5s ease;
}

.carousel-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.carousel-leave-to {
  opacity: 0;
  transform: translateX(-100%);
}

.carousel-move {
  transition: transform 0.5s ease;
}

.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1;
  transition: all 0.3s ease;
}

.carousel-arrow:hover {
  background: rgba(0, 0, 0, 0.7);
  transform: translateY(-50%) scale(1.1);
}

.carousel-arrow.left {
  left: -20px;
}

.carousel-arrow.right {
  right: -20px;
}

.playlist-item {
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
}

.playlist-item:hover {
  transform: translateY(-5px);
}

.song-cover {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
}

.song-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.playlist-item:hover .play-icon {
  opacity: 1;
}

.song-info {
  margin-top: 8px;
}

.song-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.song-artist {
  font-size: 0.9em;
  color: #666;
}

.page-indicators {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ddd;
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator:hover {
  transform: scale(1.2);
}

.indicator.active {
  background: #4f81e4;
  transform: scale(1.2);
}

.rankings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.ranking-category {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.ranking-item:hover {
  background-color: #f5f5f5;
}

.rank-number {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4f81e4;
  color: white;
  border-radius: 50%;
  margin-right: 10px;
}

.rank-info {
  flex: 1;
}

.rank-name {
  font-weight: 500;
  color: #333;
}

.rank-detail {
  font-size: 0.9em;
  color: #666;
}
</style>