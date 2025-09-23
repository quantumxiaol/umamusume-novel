// frontend/src/stores/novelStore.js
import { defineStore } from 'pinia';
import { generateNovel as apiGenerateNovel } from '@/services/api'; // @ 是 Vite 配置的路径别名，指向 src

export const useNovelStore = defineStore('novel', {
  state: () => ({
    prompt: '',
    generatedNovel: '',
    characterImage: '', 
    isLoading: false,
    error: null,
  }),

  actions: {
    setPrompt(prompt) {
      this.prompt = prompt;
    },
    async generateNovel() {
      if (!this.prompt.trim()) {
        this.error = 'Please enter a prompt.';
        return;
      }

      this.isLoading = true;
      this.error = null;
      this.generatedNovel = '';
      this.characterImage = '';

      try {
        // 调用 API 服务
        const data = await apiGenerateNovel(this.prompt);
        
        // 假设后端返回格式为 { response: "...", image_url?: "..." }
        this.generatedNovel = data.response || 'No novel content received.';
        this.characterImage = data.image_url || ''; // 如果有图片URL则设置
        
        console.log('Novel generated successfully.');
      } catch (err) {
        this.error = err.message || 'Failed to generate novel.';
        console.error('Error in store:', this.error);
      } finally {
        this.isLoading = false;
      }
    },
    clearResults() {
      this.generatedNovel = '';
      this.characterImage = '';
      this.error = null;
      // 注意：不清除 prompt，用户可能想重新生成
    }
  },
});