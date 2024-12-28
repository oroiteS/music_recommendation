// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';  // 使用 Vue 3 的 Router API
import LoginPage from '@/components/LoginPage.vue';  // 引入 LoginPage 组件
import HomePage from '@/components/HomePage.vue';
import RegisterPage from '@/components/RegisterPage.vue';
import MusicList from '@/components/music/MusicList.vue';
import MusicDetail from '../components/music/MusicDetail.vue'
import MyPlaylists from '@/components/playlist/MyPlaylists.vue';
import PlaylistDetail from '@/components/playlist/PlaylistDetail.vue';
import MusicEdit from '@/components/music/MusicEdit.vue';
import MyPage from '@/components/MyPage.vue';
import SearchResults from '@/components/SearchResults.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: LoginPage
    },
    {
        path: '/register',
        name: 'RegisterPage',
        component: RegisterPage
    },
    {
        path: '/',
        name: 'Home',
        component: HomePage,
        meta: { requiresAuth: true }  // 需要登录才能访问
    },
    {
        path: '/music-list',  // 新添加
        name: 'MusicList',
        component: MusicList
    },
    {
        path: '/music/:id',
        name: 'MusicDetail',
        component: MusicDetail
    },
    {
        path: '/my-playlists',
        name: 'MyPlaylists',
        component: MyPlaylists
    },
    {
        path: '/playlist/:id',
        name: 'PlaylistDetail',
        component: PlaylistDetail
    },
    {
        path: '/music/:id/edit',
        name: 'MusicEdit',
        component: MusicEdit,
        meta: { 
            requiresAuth: true,
            requiresAdmin: true  // 添加管理员权限要求
        }
    },
    {
        path: '/my',
        name: 'MyPage',
        component: MyPage
    },
    {
        path: '/search',
        name: 'Search',
        component: SearchResults
    }
];

const router = createRouter({
    history: createWebHistory(),  // 使用 HTML5 History 模式
    routes  // 路由配置
});

// 全局前置守卫：检查是否需要登录
router.beforeEach((to, from, next) => {
    const user = sessionStorage.getItem('user');
    let isLoggedIn = false;

    if (user) {
        try {
            const parsedUser = JSON.parse(user);
            isLoggedIn = parsedUser && parsedUser.userid && parsedUser.username;
        } catch (e) {
            console.error("Failed to parse user data in router:", e);
        }
    }

    // 如果目标路由需要登录且用户未登录
    if (to.meta.requiresAuth && !isLoggedIn) {
        // 重定向到登录页面
        next({ name: 'Login' });
    } else {
        // 允许访问页面
        next();
    }
});


export default router;
