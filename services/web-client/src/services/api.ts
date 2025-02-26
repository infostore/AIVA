import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

// API 클라이언트 설정
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 설정
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 설정
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // 토큰 만료 에러 (401) 및 재시도하지 않은 요청인 경우
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // 리프레시 토큰으로 새 액세스 토큰 요청
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          // 리프레시 토큰이 없으면 로그인 페이지로 리다이렉트
          window.location.href = '/auth/login';
          return Promise.reject(error);
        }
        
        const response = await apiClient.post('/auth/refresh', {
          refreshToken,
        });
        
        // 새 토큰 저장
        const { token } = response.data;
        localStorage.setItem('token', token);
        
        // 원래 요청 재시도
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // 리프레시 토큰도 만료된 경우 로그아웃 처리
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// 인증 서비스
export const authService = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login', { email, password });
    return response.data;
  },
  
  register: async (username: string, email: string, password: string) => {
    const response = await apiClient.post('/auth/register', { username, email, password });
    return response.data;
  },
  
  logout: async () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

// 주식 서비스
export const stockService = {
  getStocks: async (params = {}) => {
    const response = await apiClient.get('/stocks', { params });
    return response.data;
  },
  
  getStockById: async (id: string) => {
    const response = await apiClient.get(`/stocks/${id}`);
    return response.data;
  },
  
  getStockHistory: async (id: string, period: string = '1m') => {
    const response = await apiClient.get(`/stocks/${id}/history`, { params: { period } });
    return response.data;
  },
  
  getTopStocks: async () => {
    const response = await apiClient.get('/stocks/top');
    return response.data;
  },
  
  getRecentStocks: async () => {
    const response = await apiClient.get('/stocks/recent');
    return response.data;
  },
  
  searchStocks: async (query: string) => {
    const response = await apiClient.get('/stocks/search', { params: { query } });
    return response.data;
  },
};

// 알림 서비스
export const notificationService = {
  getNotifications: async () => {
    const response = await apiClient.get('/notifications');
    return response.data;
  },
  
  markAsRead: async (id: string) => {
    const response = await apiClient.patch(`/notifications/${id}/read`);
    return response.data;
  },
  
  markAllAsRead: async () => {
    const response = await apiClient.patch('/notifications/read-all');
    return response.data;
  },
  
  getSettings: async () => {
    const response = await apiClient.get('/notifications/settings');
    return response.data;
  },
  
  updateSettings: async (settings: any) => {
    const response = await apiClient.put('/notifications/settings', settings);
    return response.data;
  },
};

// 분석 서비스
export const analysisService = {
  getStockAnalysis: async (id: string) => {
    const response = await apiClient.get(`/analysis/stocks/${id}`);
    return response.data;
  },
  
  getMarketOverview: async () => {
    const response = await apiClient.get('/analysis/market');
    return response.data;
  },
};

export default apiClient; 