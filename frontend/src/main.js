import { createApp } from 'vue'
import './style.css'
import './assets/style.css'
import App from './App.vue'
import router from './router'
import Chart from 'chart.js/auto'
import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"
import "./assets/toast-theme.css"
import tokenManager from './utils/tokenManager.js'

window.Chart = Chart

const app = createApp(App)

// Configure toast options
const toastOptions = {
  position: "top-right",
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
  transition: "Vue-Toastification__bounce",
  maxToasts: 20,
  newestOnTop: true
}

app.use(router)
app.use(Toast, toastOptions)
app.mount('#app')
