// frontend/src/services/api.js
import axios from 'axios';

// 从环境变量获取基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 600秒超时，因为生成小说可能需要时间
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 调用后端 /ask 端点生成小说
 * @param {string} prompt - 用户输入的提示
 * @returns {Promise<Object>} - 包含生成小说和可能的图片URL的响应对象
 */
export const generateNovel = async (prompt) => {
  try {
    console.log(`[API] Sending request to ${API_BASE_URL}/ask with prompt:`, prompt);
    const response = await apiClient.post('/ask', { question: prompt });
    console.log('[API] Received response:', response.data);
    return {
        response: response.data.answer || 'No answer received from server.',
        // image_url: response.data.image_url || '' // 如果后端未来会返回，可以加上
    };
  } catch (error) {
    console.error('[API] Error generating novel:', error);
    if (error.response) {
        // 服务器返回了错误状态码
        throw new Error(`Server Error: ${error.response.status} - ${error.response.data?.detail || 'Unknown error'}`);
    } else if (error.request) {
        // 请求已发出但没有收到响应
        throw new Error('Network Error: No response received from server.');
    } else {
        // 其他错误
        throw new Error(`Request Error: ${error.message}`);
    }
  }
};

// 未来预留的 API 调用 (如果后端实现了)
// export const generateImagePrompt = async (novelSegment) => { ... };
// export const generateVideoPrompt = async (novelSegment) => { ... };