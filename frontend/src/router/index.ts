import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LabView from '@/views/LabView.vue'
// 這裡補上了缺少的引入
import BlogView from '@/views/BlogView.vue'
import PostDetailView from '@/views/PostDetailView.vue'

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
    }, // 這裡補上了逗號，解決 TS(1005) 錯誤
    {
      path: '/blog',
      name: 'blog',
      component: BlogView
    },
    {
      path: '/blog/:id',
      name: 'post-detail',
      component: PostDetailView
    }
  ]
})

export default router