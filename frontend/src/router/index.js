import { createRouter, createWebHistory } from 'vue-router'
import Homepage from '../components/Homepage.vue'
import logreg from '../components/logreg.vue'
import userdash from '../components/userdash.vue'
import userProfile from '../components/userProfile.vue'
import userHistory from '../components/userHistory.vue'
import userfb from '../components/userfb.vue'
import admindash from '../components/admindash.vue'

const routes = [
  {
    path: '/',
    name: 'Homepage',
    component: Homepage
  },
  {
    path: '/login',
    name: 'Login',
    component: logreg
  },
  {
    path: '/dashboard',
    name: 'userdash',
    component: userdash,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'userProfile',
    component: userProfile,
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'userHistory',
    component: userHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/feedback',
    name: 'userfb',
    component: userfb,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'admindash',
    component: admindash,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'adminUsers',
    component: () => import('../components/adminUsers.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/records',
    name: 'adminRec',
    component: () => import('../components/adminRec.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/feedback',
    name: 'adminfb',
    component: () => import('../components/adminfb.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const urole = localStorage.getItem('user_role')

  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  if (to.meta.requiresAdmin && urole !== 'admin') {
    next('/dashboard')
    return
  }
  next()
})

export default router