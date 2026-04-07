import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

async function performRefresh(): Promise<string> {
  const refreshToken = localStorage.getItem('admin_refresh_token');
  if (!refreshToken) throw new Error('no refresh token');
  // Use bare axios here (not `api`) to avoid recursive interceptors
  const res = await axios.post(
    (import.meta.env.VITE_API_BASE_URL ?? '') + '/api/refresh',
    { refresh_token: refreshToken }
  );
  localStorage.setItem('admin_token', res.data.access_token);
  localStorage.setItem('admin_refresh_token', res.data.refresh_token);
  return res.data.access_token;
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !original.url?.includes('/api/refresh') &&
      !original.url?.includes('/api/login')
    ) {
      original._retry = true;
      try {
        if (!isRefreshing) {
          isRefreshing = true;
          refreshPromise = performRefresh().finally(() => {
            isRefreshing = false;
          });
        }
        const newToken = await refreshPromise!;
        if (original.headers) {
          original.headers.Authorization = `Bearer ${newToken}`;
        }
        return api(original);
      } catch {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_refresh_token');
        if (!window.location.hash.includes('/login')) {
          window.location.href = import.meta.env.BASE_URL + 'login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
