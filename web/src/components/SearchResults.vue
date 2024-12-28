<template>
  <div class="search-results">
    <h2>搜索结果: "{{ searchQuery }}"</h2>
    
    <div v-if="results.length > 0" class="results-grid">
      <div v-for="song in results" 
           :key="song.id" 
           class="result-item"
           @click="playSong(song.id)">
        <div class="song-cover">
          <img :src="song.cover" :alt="song.title">
          <div class="play-icon">▶</div>
        </div>
        <div class="song-info">
          <div class="song-title">{{ song.title }}</div>
          <div class="song-artist">{{ song.artist }}</div>
        </div>
      </div>
    </div>
    
    <div v-else class="no-results">
      未找到相关歌曲
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();
    const results = ref([]);
    const searchQuery = ref('');

    const loadResults = async () => {
      try {
        searchQuery.value = route.query.q || '';
        if (!searchQuery.value) return;

        const response = await axios.get('http://localhost:5000/search', {
          params: { query: searchQuery.value }
        });

        if (response.data.success) {
          results.value = response.data.results;
        }
      } catch (error) {
        console.error('搜索失败:', error);
      }
    };

    // 监听路由查询参数的变化
    watch(
      () => route.query.q,
      (newQuery) => {
        if (newQuery) {
          loadResults();
        }
      }
    );

    const playSong = (songId) => {
      router.push(`/music/${songId}`);
    };

    // 初始加载
    loadResults();

    return {
      results,
      searchQuery,
      playSong
    };
  }
};
</script>

<style scoped>
.search-results {
  padding: 20px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.result-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.result-item:hover {
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
  transition: opacity 0.2s;
}

.result-item:hover .play-icon {
  opacity: 1;
}

.song-info {
  margin-top: 8px;
}

.song-title {
  font-weight: 500;
  color: #333;
}

.song-artist {
  font-size: 0.9em;
  color: #666;
}

.no-results {
  text-align: center;
  color: #666;
  margin-top: 40px;
  font-size: 1.1em;
}
</style> 