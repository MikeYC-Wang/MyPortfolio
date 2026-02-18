import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LabView from '@/views/LabView.vue'
import BlogView from '@/views/BlogView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import AdminView from '@/views/AdminView.vue' // 引入後台管理頁面

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/lab',
      name: 'lab',
      component: LabView
    },
    {
      path: '/blog',
      name: 'blog',
      component: BlogView
    },
    {
      path: '/blog/:id',
      name: 'post-detail',
      component: PostDetailView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView
    }
  ]
})

export default router