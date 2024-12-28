<template>
  <div id="app">
    <div id="body">
      <!-- 导航栏 -->
      <nav v-if="!isLoginPage">
        <router-link to="/">音乐馆</router-link> |
        <router-link to="/music-list">音乐列表</router-link> |
        <router-link to="/my-playlists">我的歌单</router-link> |
        <input type="text" v-model="searchQuery" placeholder="搜索音乐" @keyup.enter="handleSearch" />
        <router-link to="/my">我的</router-link>
      </nav>

      <div class="main-content">
        <!-- 动态加载路由内容 -->
        <transition name="fade">
          <router-view /> <!-- 根据路由渲染相应的组件 -->
        </transition>
      </div>
      <MusicPlayer v-if="!isLoginPage && isLoggedIn" ref="player" />
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MusicPlayer from './components/music/MusicPlayer.vue';

export default {
  components: {
    MusicPlayer  // 注册MusicPlayer组件
  },
  setup() {  // Vue3的组合式API入口函数
    const route = useRoute();  // 获取当前路由对象
    const router = useRouter();  // 获取路由器实例

    // 计算属性：判断是否为登录/注册页面
    const isLoginPage = computed(() => {
      return route.path === '/login' || route.path === '/register';
    });

    // 计算属性：判断用户是否已登录
    const isLoggedIn = computed(() => {
      return !!sessionStorage.getItem('user');
    });

    const searchQuery = ref('');  // 创建响应式的搜索查询变量

    // 处理搜索功能
    const handleSearch = () => {
      if (searchQuery.value.trim()) {
        router.push({
          path: '/search',
          query: { q: searchQuery.value.trim() }
        });
      }
    };

    // 返回需要在模板中使用的数据和方法
    return {
      isLoginPage,
      isLoggedIn,
      searchQuery,
      handleSearch
    };
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  display: flex;
  align-items: center;
  justify-content: center;
}
#body {
  width: 1500px;
}
.main-content {
  padding-bottom: 100px;
  min-height: calc(100vh - 160px);
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}

nav a.router-link-exact-active {
  color: #42b983;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.content-container {
  padding-bottom: 100px;
}

/* 淡入淡出过渡效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active in <2.1.8 */ {
  opacity: 0;
}
</style>