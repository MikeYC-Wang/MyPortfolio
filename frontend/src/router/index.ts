import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LabView from '@/views/LabView.vue'
import BlogView from '@/views/BlogView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import AdminView from '@/views/AdminView.vue'
import LoginView from '@/views/LoginView.vue'
import LabEditorView from '@/views/LabEditorView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ProjectView from '@/views/ProjectView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/lab', name: 'lab', component: LabView },
    { 
      path: '/lab/new', 
      name: 'lab-new', 
      component: LabEditorView 
    },
    { 
      path: '/lab/edit/:slug',
      name: 'lab-edit', 
      component: LabEditorView 
    },
    { path: '/blog', name: 'blog', component: BlogView },
    { path: '/blog/:id', name: 'post-detail', component: PostDetailView },
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true } 
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectView
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    }
  ],

  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      // 點擊瀏覽器上一頁/下一頁時，回到原本的位置
      return savedPosition;
    } else {
      // 切換到新頁面時，強制回到最上方
      return { top: 0 };
    }
  }
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('admin_token');
    
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