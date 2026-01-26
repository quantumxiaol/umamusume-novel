<!-- frontend/src/App.vue -->
<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useNovelStore } from '@/stores/novelStore';
import LanguageSelector from './components/LanguageSelector.vue';
import HistoryDrawer from './components/HistoryDrawer.vue';
import { onMounted } from 'vue';

const { t } = useI18n();
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
const showHistory = ref(false);

// 初始化
onMounted(() => {
  novelStore.initHistory();
});

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

// 处理保存到历史
const handleSaveToHistory = () => {
  novelStore.saveToHistory();
  // 可以添加一个简单的提示
  alert(t('status.saved'));
};

// 处理下载 MD
const handleDownload = () => {
  const content = novelStore.generatedNovel;
  if (!content) return;

  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `novel-${new Date().toISOString().slice(0, 10)}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

</script>

<template>
  <div id="app">
    <div class="background-overlay"></div>
    <div class="container">
      <header>
        <div class="header-content">
          <h1>{{ t('app.title') }}</h1>
          <div class="header-actions">
            <button class="history-btn" @click="showHistory = true">
              {{ t('buttons.history') }}
            </button>
            <LanguageSelector />
          </div>
        </div>
      </header>

      <main>
        <div class="input-section">
          <label for="prompt-input">{{ t('input.label') }}</label>
          <textarea
            id="prompt-input"
            v-model="localPrompt"
            :disabled="isLoading"
            :placeholder="t('input.placeholder')"
            rows="6"
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
              <span>{{ t('input.streamMode') }}</span>
            </label>
          </div>
          <div class="button-group">
            <button @click="handleGenerate" :disabled="isLoading || !localPrompt.trim()">
              {{ isLoading ? t('buttons.generating') : t('buttons.generate') }}
            </button>
            <button 
              v-if="isLoading && streamMode" 
              @click="handleCancel" 
              class="cancel-button"
            >
              {{ t('buttons.cancel') }}
            </button>
            <button @click="handleClear" :disabled="isLoading">
              {{ t('buttons.clear') }}
            </button>
          </div>
          <div v-if="error" class="error-message">
            {{ t('status.error') }}: {{ error }}
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
              <h3>{{ t('output.ragResult') }}</h3>
              <span class="result-length">({{ ragResult.length }} {{ t('output.characters') }})</span>
            </div>
            <div v-show="showRagResult" class="collapsible-content">
              <pre class="result-text">{{ ragResult }}</pre>
            </div>
          </div>

          <!-- Web 搜索结果（可折叠） -->
          <div class="collapsible-section" v-if="webResult">
            <div class="collapsible-header" @click="showWebResult = !showWebResult">
              <span class="toggle-icon">{{ showWebResult ? '▼' : '▶' }}</span>
              <h3>{{ t('output.webResult') }}</h3>
              <span class="result-length">({{ webResult.length }} {{ t('output.characters') }})</span>
            </div>
            <div v-show="showWebResult" class="collapsible-content">
              <pre class="result-text">{{ webResult }}</pre>
            </div>
          </div>

          <!-- 生成的小说 -->
          <div class="novel-output" v-if="generatedNovel || (isLoading && streamMode)">
            <div class="output-header">
              <h2>{{ t('output.novel') }}</h2>
              <div class="output-actions">
                <button 
                  v-if="generatedNovel && !isLoading" 
                  @click="handleSaveToHistory" 
                  class="action-btn save-btn"
                >
                  {{ t('buttons.save') }}
                </button>
                <button 
                  v-if="generatedNovel && !isLoading" 
                  @click="handleDownload" 
                  class="action-btn download-btn"
                >
                  {{ t('buttons.download') }}
                </button>
              </div>
            </div>
            <pre class="novel-text" :class="{ 'streaming': isLoading && streamMode }">
              {{ generatedNovel || (isLoading && streamMode ? t('status.generating') : '') }}
            </pre>
            <div v-if="isLoading && streamMode" class="streaming-indicator">
              <span class="dot"></span>
              <span>{{ t('status.streaming') }}</span>
            </div>
          </div>

          <!-- 角色图片 -->
          <div class="image-output" v-if="characterImage">
            <h2>{{ t('output.characterImage') }}</h2>
            <img :src="characterImage" alt="Character Image" class="character-image" />
          </div>
        </div>
      </main>
    </div>
    <HistoryDrawer :is-open="showHistory" @close="showHistory = false" />
  </div>
</template>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  min-height: 100vh;
  position: relative;
  background-image: url('/background.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

/* 背景虚化遮罩层 */
.background-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 1;
}

/* 主容器 */
.container {
  position: relative;
  z-index: 2;
  max-width: 1400px;
  width: 90%;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
}

header {
  margin-bottom: 30px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  gap: 20px;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.history-btn {
  background-color: transparent;
  border: 1px solid #42b983;
  color: #42b983;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.history-btn:hover {
  background-color: #42b983;
  color: white;
}

header h1 {
  margin: 0;
  font-size: 2.5em;
  color: #2c3e50;
  text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.8);
  flex: 1;
  min-width: 300px;
}

.input-section {
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.input-section label {
  display: block;
  margin-bottom: 12px;
  font-weight: bold;
  font-size: 18px;
  text-align: left;
}

.input-section textarea {
  width: 100%;
  padding: 15px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
  min-height: 120px;
}

.input-section textarea:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
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
  padding: 12px 28px;
  margin-right: 12px;
  margin-top: 10px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  background-color: #42b983;
  color: white;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.button-group button:hover:not(:disabled) {
  background-color: #359c6d;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.button-group button:active:not(:disabled) {
  transform: translateY(0);
}

.button-group button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  box-shadow: none;
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
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}



.output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #42b983;
  margin-top: 20px;
  margin-bottom: 15px;
  padding-bottom: 10px;
}

.output-header h2 {
  border-bottom: none;
  padding-bottom: 0;
  margin-top: 0;
  margin-bottom: 0;
  font-size: 1.5em;
  color: #2c3e50;
}

.output-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 5px 15px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: white;
  transition: opacity 0.2s;
}

.action-btn:hover {
  opacity: 0.9;
}

.save-btn {
  background-color: #3498db;
}

.download-btn {
  background-color: #9b59b6;
}

.novel-text {
  white-space: pre-wrap;
  background-color: #f9f9f9;
  padding: 25px;
  border: 2px solid #ddd;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 16px;
  line-height: 1.8;
  min-height: 300px;
  max-height: 70vh;
  overflow-y: auto;
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
  border: 2px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
}

.collapsible-header {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background-color: rgba(245, 245, 245, 0.9);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.collapsible-header:hover {
  background-color: rgba(232, 232, 232, 0.9);
}

.collapsible-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
}

.toggle-icon {
  margin-right: 12px;
  color: #42b983;
  font-size: 16px;
  transition: transform 0.2s ease;
}

.result-length {
  font-size: 13px;
  color: #999;
  margin-left: 10px;
}

.collapsible-content {
  padding: 20px;
  background-color: rgba(250, 250, 250, 0.9);
  border-top: 2px solid #ddd;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

.result-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #fff;
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  max-height: 60vh;
  overflow-y: auto;
  font-size: 15px;
  line-height: 1.8;
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .container {
    max-width: 95%;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  header h1 {
    font-size: 2em;
    text-align: center;
    min-width: auto;
  }
  
  .container {
    width: 95%;
    padding: 20px 10px;
  }
  
  .input-section,
  .output-section {
    padding: 20px;
  }
  
  .input-section textarea {
    min-height: 100px;
    font-size: 14px;
  }
  
  .button-group button {
    padding: 10px 20px;
    font-size: 14px;
    margin-right: 8px;
  }
  
  .novel-text,
  .result-text {
    font-size: 14px;
    padding: 15px;
  }
  
  .collapsible-header h3 {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  header h1 {
    font-size: 1.5em;
  }
  
  .input-section label {
    font-size: 16px;
  }
  
  .button-group button {
    width: 100%;
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style>