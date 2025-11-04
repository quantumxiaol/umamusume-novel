<!-- frontend/src/App.vue -->
<script setup>
import { ref, computed } from 'vue';
import { useNovelStore } from '@/stores/novelStore';

const novelStore = useNovelStore();

// 计算属性，方便在模板中使用状态
const prompt = computed(() => novelStore.prompt);
const generatedNovel = computed(() => novelStore.generatedNovel);
const characterImage = computed(() => novelStore.characterImage);
const isLoading = computed(() => novelStore.isLoading);
const error = computed(() => novelStore.error);
const streamMode = computed(() => novelStore.streamMode);
const currentStatus = computed(() => novelStore.currentStatus);
const ragResult = computed(() => novelStore.ragResult);
const webResult = computed(() => novelStore.webResult);

// 本地响应式引用，用于绑定输入框
const localPrompt = ref(novelStore.prompt);

// 折叠状态
const showRagResult = ref(false);
const showWebResult = ref(false);

// 处理输入变化
const handlePromptInput = (event) => {
  localPrompt.value = event.target.value;
};

// 处理流式模式切换
const handleStreamModeToggle = (event) => {
  novelStore.setStreamMode(event.target.checked);
};

// 处理生成按钮点击
const handleGenerate = () => {
  novelStore.setPrompt(localPrompt.value);
  novelStore.generateNovel();
};

// 处理取消流式请求
const handleCancel = () => {
  novelStore.cancelStream();
};

// 处理清除按钮点击
const handleClear = () => {
  localPrompt.value = '';
  novelStore.setPrompt('');
  novelStore.clearResults();
};
</script>

<template>
  <div id="app">
    <header>
      <h1>赛马娘同人小说生成器</h1>
    </header>

    <main>
      <div class="input-section">
        <label for="prompt-input">输入你的创作指令:</label>
        <textarea
          id="prompt-input"
          v-model="localPrompt"
          :disabled="isLoading"
          placeholder="例如：请写一篇关于无声铃鹿在训练中遇到挫折，但最终克服困难的故事。"
          rows="4"
          cols="50"
        ></textarea>
        <div class="mode-toggle">
          <label class="toggle-label">
            <input
              type="checkbox"
              :checked="streamMode"
              @change="handleStreamModeToggle"
              :disabled="isLoading"
            />
            <span>流式模式（实时显示生成内容）</span>
          </label>
        </div>
        <div class="button-group">
          <button @click="handleGenerate" :disabled="isLoading || !localPrompt.trim()">
            {{ isLoading ? (streamMode ? '生成中...' : '生成中...') : '生成小说' }}
          </button>
          <button 
            v-if="isLoading && streamMode" 
            @click="handleCancel" 
            class="cancel-button"
          >
            取消生成
          </button>
          <button @click="handleClear" :disabled="isLoading">
            清除结果
          </button>
        </div>
        <div v-if="error" class="error-message">
          错误: {{ error }}
        </div>
        <div v-if="currentStatus && streamMode" class="status-message">
          {{ currentStatus }}
        </div>
      </div>

      <div class="output-section" v-if="generatedNovel || characterImage || isLoading || ragResult || webResult">
        <!-- RAG 搜索结果（可折叠） -->
        <div class="collapsible-section" v-if="ragResult">
          <div class="collapsible-header" @click="showRagResult = !showRagResult">
            <span class="toggle-icon">{{ showRagResult ? '▼' : '▶' }}</span>
            <h3>RAG 搜索结果</h3>
            <span class="result-length">({{ ragResult.length }} 字符)</span>
          </div>
          <div v-show="showRagResult" class="collapsible-content">
            <pre class="result-text">{{ ragResult }}</pre>
          </div>
        </div>

        <!-- Web 搜索结果（可折叠） -->
        <div class="collapsible-section" v-if="webResult">
          <div class="collapsible-header" @click="showWebResult = !showWebResult">
            <span class="toggle-icon">{{ showWebResult ? '▼' : '▶' }}</span>
            <h3>Web 搜索结果</h3>
            <span class="result-length">({{ webResult.length }} 字符)</span>
          </div>
          <div v-show="showWebResult" class="collapsible-content">
            <pre class="result-text">{{ webResult }}</pre>
          </div>
        </div>

        <!-- 生成的小说 -->
        <div class="novel-output" v-if="generatedNovel || (isLoading && streamMode)">
          <h2>生成的小说:</h2>
          <pre class="novel-text" :class="{ 'streaming': isLoading && streamMode }">
            {{ generatedNovel || (isLoading && streamMode ? '正在生成中...' : '') }}
          </pre>
          <div v-if="isLoading && streamMode" class="streaming-indicator">
            <span class="dot"></span>
            <span>正在流式生成中...</span>
          </div>
        </div>

        <!-- 角色图片 -->
        <div class="image-output" v-if="characterImage">
          <h2>角色图片:</h2>
          <img :src="characterImage" alt="Character Image" class="character-image" />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  max-width: 800px;
  margin: 60px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

header h1 {
  margin-bottom: 20px;
}

.input-section {
  margin-bottom: 30px;
}

.input-section label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
}

.input-section textarea {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
  box-sizing: border-box;
}

.button-group {
  margin-top: 15px;
}

.mode-toggle {
  margin-top: 10px;
  margin-bottom: 10px;
}

.toggle-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.toggle-label input[type="checkbox"] {
  margin-right: 8px;
  cursor: pointer;
}

.toggle-label span {
  font-size: 14px;
  color: #2c3e50;
}

.button-group button {
  padding: 10px 20px;
  margin-right: 10px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #42b983;
  color: white;
}

.button-group button:hover:not(:disabled) {
  background-color: #359c6d;
}

.button-group button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.cancel-button {
  background-color: #e74c3c !important;
}

.cancel-button:hover:not(:disabled) {
  background-color: #c0392b !important;
}

.error-message {
  color: red;
  margin-top: 10px;
  font-weight: bold;
}

.status-message {
  color: #42b983;
  margin-top: 10px;
  font-weight: 500;
  font-size: 14px;
  padding: 8px 12px;
  background-color: #f0f9f5;
  border-left: 3px solid #42b983;
  border-radius: 4px;
}

.output-section {
  text-align: left;
}

.output-section h2 {
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
  margin-top: 20px;
}

.novel-text {
  white-space: pre-wrap; /* 保留换行和空格 */
  background-color: #f9f9f9;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-x: auto; /* 如果内容太宽 */
}

.character-image {
  max-width: 100%;
  height: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 10px;
}

.novel-text.streaming {
  position: relative;
}

.streaming-indicator {
  display: flex;
  align-items: center;
  margin-top: 10px;
  color: #42b983;
  font-size: 14px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #42b983;
  margin-right: 8px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 可折叠区域样式 */
.collapsible-section {
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.collapsible-header {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background-color: #f5f5f5;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.collapsible-header:hover {
  background-color: #e8e8e8;
}

.collapsible-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
}

.toggle-icon {
  margin-right: 10px;
  color: #42b983;
  font-size: 14px;
  transition: transform 0.2s ease;
}

.result-length {
  font-size: 12px;
  color: #999;
  margin-left: 10px;
}

.collapsible-content {
  padding: 15px;
  background-color: #fafafa;
  border-top: 1px solid #ddd;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}

.result-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #fff;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  margin: 0;
}

/* 美化滚动条 */
.result-text::-webkit-scrollbar {
  width: 8px;
}

.result-text::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.result-text::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.result-text::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>