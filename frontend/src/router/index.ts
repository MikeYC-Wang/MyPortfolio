import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LabView from '@/views/LabView.vue'
import BlogView from '@/views/BlogView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import AdminView from '@/views/AdminView.vue'
import LoginView from '@/views/LoginView.vue' // ✨ 1. 引入 LoginView

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/lab', name: 'lab', component: LabView },
    { path: '/blog', name: 'blog', component: BlogView },
    { path: '/blog/:id', name: 'post-detail', component: PostDetailView },
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true } 
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = sessionStorage.getItem('admin_token');
    
    if (token) {
      next();
    } else {
      next('/login');
    }
  } else {
    next();
  }
});

export default router