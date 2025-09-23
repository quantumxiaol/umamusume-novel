// frontend/src/main.js
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
// 如果使用了 Vue Router
// import router from './router'; // 创建了 src/router/index.js

const app = createApp(App);

app.use(createPinia());
// if using router
// app.use(router);

app.mount('#app');