// frontend/src/stores/novelStore.js
import { defineStore } from 'pinia';
import { generateNovel as apiGenerateNovel, generateNovelStream } from '@/services/api'; // @ 是 Vite 配置的路径别名，指向 src

export const useNovelStore = defineStore('novel', {
  state: () => ({
    prompt: '',
    generatedNovel: '',
    characterImage: '',
    isLoading: false,
    error: null,
    streamMode: false, // 是否使用流式模式
    streamCancelled: false, // 是否取消流式请求
    currentStatus: '', // 当前状态信息（用于显示进度）
    ragResult: '', // RAG 搜索结果
    ragResult: '', // RAG 搜索结果
    webResult: '', // Web 搜索结果
    history: [], // 历史记录
  }),

  actions: {
    setPrompt(prompt) {
      this.prompt = prompt;
    },
    setStreamMode(mode) {
      this.streamMode = mode;
    },
    async generateNovel() {
      if (!this.prompt.trim()) {
        this.error = '请输入提示词。';
        return;
      }

      this.isLoading = true;
      this.error = null;
      this.generatedNovel = '';
      this.characterImage = '';
      this.streamCancelled = false;
      this.currentStatus = '';
      this.ragResult = '';
      this.webResult = '';

      try {
        if (this.streamMode) {
          // 流式生成
          await this.generateNovelStream();
        } else {
          // 非流式生成
          const data = await apiGenerateNovel(this.prompt);

          // 假设后端返回格式为 { response: "...", image_url?: "..." }
          this.generatedNovel = data.response || '未收到小说内容。';
          this.characterImage = data.image_url || ''; // 如果有图片URL则设置

          console.log('Novel generated successfully.');
        }
      } catch (err) {
        if (!this.streamCancelled) {
          this.error = err.message || '生成小说失败。';
          console.error('Error in store:', this.error);
        }
      } finally {
        this.isLoading = false;
      }
    },
    async generateNovelStream() {
      // 流式生成小说
      let novelContent = '';

      await generateNovelStream(this.prompt, (eventData) => {
        if (this.streamCancelled) {
          return;
        }

        const { event, data } = eventData;

        switch (event) {
          case 'status':
            // 显示当前状态
            this.currentStatus = data || '';
            console.log('[Store] Status:', this.currentStatus);
            break;

          case 'rag_result':
            this.ragResult = data || '';
            console.log('[Store] RAG result received, length:', this.ragResult.length);
            break;

          case 'web_result':
            this.webResult = data || '';
            console.log('[Store] Web result received, length:', this.webResult.length);
            break;

          case 'token':
            // 流式接收小说内容
            if (data) {
              novelContent += data;
              this.generatedNovel = novelContent;
              // 清除状态信息，因为开始生成小说了
              if (this.currentStatus && this.currentStatus.includes('开始生成小说')) {
                this.currentStatus = '正在生成小说...';
              }
            }
            break;

          case 'done':
            console.log('[Store] Stream completed');
            this.currentStatus = '生成完成！';
            this.isLoading = false;
            break;

          case 'error':
            this.error = data || '流式生成过程中发生错误。';
            this.currentStatus = '';
            console.error('[Store] Stream error:', this.error);
            this.isLoading = false;
            break;

          default:
            console.warn('[Store] Unknown event:', event);
        }
      });
    },
    cancelStream() {
      // 取消流式请求
      this.streamCancelled = true;
      this.isLoading = false;
    },
    clearResults() {
      this.generatedNovel = '';
      this.characterImage = '';
      this.error = null;
      this.streamCancelled = false;
      this.currentStatus = '';
      this.ragResult = '';
      this.webResult = '';
      // 注意：不清除 prompt，用户可能想重新生成
    },
    // 历史记录相关 Action
    initHistory() {
      const storedHistory = localStorage.getItem('novelHistory');
      if (storedHistory) {
        try {
          this.history = JSON.parse(storedHistory);
        } catch (e) {
          console.error('Failed to parse history from localStorage', e);
          this.history = [];
        }
      }
    },
    saveToHistory() {
      if (!this.prompt && !this.generatedNovel) return;

      const newEntry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        prompt: this.prompt,
        generatedNovel: this.generatedNovel,
        characterImage: this.characterImage,
        ragResult: this.ragResult,
        webResult: this.webResult,
      };

      this.history.unshift(newEntry);
      this.persistHistory();
    },
    loadFromHistory(entry) {
      if (!entry) return;

      this.prompt = entry.prompt || '';
      this.generatedNovel = entry.generatedNovel || '';
      this.characterImage = entry.characterImage || '';
      this.ragResult = entry.ragResult || '';
      this.webResult = entry.webResult || '';
      this.currentStatus = '已加载历史记录';
    },
    deleteFromHistory(id) {
      this.history = this.history.filter(item => item.id !== id);
      this.persistHistory();
    },
    clearHistory() {
      this.history = [];
      this.persistHistory();
    },
    persistHistory() {
      localStorage.setItem('novelHistory', JSON.stringify(this.history));
    }
  },
});