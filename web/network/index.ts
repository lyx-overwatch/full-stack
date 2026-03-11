import { refresh } from 'next/cache';
import { toast } from 'sonner';
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

const ACCESS_TOKEN_EXPIRED_CODE = 40101;
const ACCESS_TOKEN_INVALID_CODE = 40102;
const AUTH_USER_INVALID_CODE = 40103;
const REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE = 40104;

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
  withAuth?: boolean;
  _retriedAfterRefresh?: boolean;
}

const getAccessToken = () => {
  if (typeof window === 'undefined') {
    return '';
  }
  return localStorage.getItem('token') || '';
};

const getRefreshToken = () => {
  if (typeof window === 'undefined') {
    return '';
  }
  return localStorage.getItem('refresh_token') || '';
};

const clearTokenAndRedirectToLogin = (
  message = '登录状态已失效，请重新登录',
) => {
  if (typeof window === 'undefined') {
    return;
  }

  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token'); 
  toast.error(message);

  // if (window.location.pathname !== '/') {
  //   window.location.href = '/';
  // }
};

const parseErrorPayload = (raw: string, fallback: string) => {
  try {
    const parsed = JSON.parse(raw) as { msg?: string; code?: number };
    return {
      code: parsed.code,
      message: parsed.msg || fallback,
    };
  } catch {
    return {
      code: undefined,
      message: raw || fallback,
    };
  }
};

const extractAccessToken = (payload: unknown) => {
  if (!payload || typeof payload !== 'object') {
    return '';
  }

  const result = payload as {
    access_token?: string;
    token?: string;
    data?: { access_token?: string; token?: string };
  };

  return (
    result.data?.access_token ||
    result.data?.token ||
    result.access_token ||
    result.token ||
    ''
  );
};

let refreshPromise: Promise<string | null> | null = null;

const refreshAccessToken = async (refreshToken: string) => {
  if (typeof window === 'undefined') {
    return null;
  }

  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const refreshUrl = `${BASE_URL}/refresh`;
      const response = await post(refreshUrl, {
        refresh_token: refreshToken,
      });

      if (!response) {
        return null;
      }

      const newToken = extractAccessToken(response);
      if (!newToken) {
        return null;
      }

      localStorage.setItem('token', newToken);
      return newToken;
    } catch {
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
};

// 通用请求函数
async function request<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const {
    headers,
    withAuth = true,
    _retriedAfterRefresh = false,
    ...customConfig
  } = options;
  const token = getAccessToken();
  const refreshToken = getRefreshToken();
  const shouldAttachAuth = withAuth && token;

  const config: RequestInit = {
    ...customConfig,
    headers: {
      'Content-Type': 'application/json',
      ...(shouldAttachAuth ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  };

  // 处理 URL，防止双斜杠等问题，或者直接拼接
  const url = endpoint.startsWith('http')
    ? endpoint
    : `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      // 尝试解析错误信息，如果解析失败则使用状态文本
      const errorText = await response.text().catch(() => response.statusText);

      const { code: errorCode, message: errorMessage } = parseErrorPayload(
        errorText,
        response.statusText,
      );

      if (response.status === 401) {
        if (
          errorCode === ACCESS_TOKEN_EXPIRED_CODE &&
          withAuth &&
          !_retriedAfterRefresh
        ) {
          const refreshedToken = await refreshAccessToken(refreshToken);
          if (refreshedToken) {
            return request<T>(endpoint, {
              ...options,
              _retriedAfterRefresh: true,
            });
          }
        }

        if (
          errorCode === ACCESS_TOKEN_INVALID_CODE ||
          errorCode === AUTH_USER_INVALID_CODE ||
          errorCode === REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE
        ) {
          clearTokenAndRedirectToLogin('登录已失效，请重新登录');
        } else {
          toast.error(errorMessage);
        }

        return Promise.reject(
          new Error(
            `HTTP error! status: ${response.status}, code: ${String(errorCode)}, message: ${errorMessage}`,
          ),
        );
      }

      toast.error(errorMessage);

      return Promise.reject(
        new Error(
          `HTTP error! status: ${response.status}, message: ${errorMessage}`,
        ),
      );
    }

    // 如果响应没有内容（例如 204 No Content），返回 null 或空对象
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    console.error('API Request Failed:', error);
    throw error;
  }
}

// GET 请求
export const get = <T>(endpoint: string, options?: RequestOptions) => {
  return request<T>(endpoint, { method: 'GET', ...options });
};

// POST 请求
export const post = <T>(
  endpoint: string,
  body: unknown,
  options?: RequestOptions,
) => {
  return request<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
    ...options,
  });
};

// PUT 请求
export const put = <T>(
  endpoint: string,
  body: unknown,
  options?: RequestOptions,
) => {
  return request<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(body),
    ...options,
  });
};

// DELETE 请求
export const del = <T>(endpoint: string, options?: RequestOptions) => {
  return request<T>(endpoint, { method: 'DELETE', ...options });
};

// PATCH 请求
export const patch = <T>(
  endpoint: string,
  body: unknown,
  options?: RequestOptions,
) => {
  return request<T>(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(body),
    ...options,
  });
};
