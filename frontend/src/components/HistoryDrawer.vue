<script setup>
import { computed } from 'vue';
import { useNovelStore } from '@/stores/novelStore';
import { useI18n } from 'vue-i18n';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close']);

const { t } = useI18n();
const novelStore = useNovelStore();

const history = computed(() => novelStore.history);

const formatDate = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleString();
};

const handleLoad = (entry) => {
  if (confirm(t('history.confirmLoad'))) {
    novelStore.loadFromHistory(entry);
    emit('close');
  }
};

const handleDelete = (id) => {
  if (confirm(t('history.confirmDelete'))) {
    novelStore.deleteFromHistory(id);
  }
};

const handleClearAll = () => {
  if (confirm(t('history.confirmClearAll'))) {
    novelStore.clearHistory();
  }
};
</script>

<template>
  <div class="drawer-overlay" :class="{ 'open': isOpen }" @click="emit('close')"></div>
  <div class="drawer" :class="{ 'open': isOpen }">
    <div class="drawer-header">
      <h2>{{ t('history.title') }}</h2>
      <button class="close-btn" @click="emit('close')">×</button>
    </div>
    
    <div class="drawer-actions" v-if="history.length > 0">
      <button class="clear-btn" @click="handleClearAll">{{ t('history.clearAll') }}</button>
    </div>

    <div class="drawer-content">
      <div v-if="history.length === 0" class="empty-state">
        {{ t('history.empty') }}
      </div>
      
      <div v-else class="history-list">
        <div v-for="item in history" :key="item.id" class="history-item">
          <div class="item-header">
            <span class="timestamp">{{ formatDate(item.timestamp) }}</span>
            <button class="delete-btn" @click="handleDelete(item.id)">{{ t('buttons.delete') }}</button>
          </div>
          <div class="item-prompt">
            {{ item.prompt.slice(0, 100) }}{{ item.prompt.length > 100 ? '...' : '' }}
          </div>
          <button class="load-btn" @click="handleLoad(item)">{{ t('history.load') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.drawer-overlay.open {
  opacity: 1;
  visibility: visible;
}

.drawer {
  position: fixed;
  top: 0;
  right: -400px;
  width: 400px;
  max-width: 90%;
  height: 100%;
  background: white;
  z-index: 999;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  display: flex;
  flex-direction: column;
}

.drawer.open {
  right: 0;
}

.drawer-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.drawer-actions {
  padding: 10px 20px;
  border-bottom: 1px solid #eee;
  text-align: right;
}

.clear-btn {
  background-color: #ff4757;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.clear-btn:hover {
  background-color: #ff6b81;
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  text-align: center;
  color: #999;
  margin-top: 50px;
}

.history-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  border: 1px solid #eee;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.timestamp {
  font-size: 12px;
  color: #666;
}

.delete-btn {
  background: none;
  border: none;
  color: #ff4757;
  cursor: pointer;
  font-size: 12px;
}

.delete-btn:hover {
  text-decoration: underline;
}

.item-prompt {
  font-size: 14px;
  color: #333;
  margin-bottom: 10px;
  line-height: 1.4;
}

.load-btn {
  width: 100%;
  background-color: #42b983;
  color: white;
  border: none;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.load-btn:hover {
  background-color: #3aa876;
}
</style>
