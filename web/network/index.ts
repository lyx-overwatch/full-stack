const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
import { toast } from 'sonner';

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

// 通用请求函数
async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { headers, ...customConfig } = options;

  const config: RequestInit = {
    ...customConfig,
    headers: {
      'Content-Type': 'application/json',
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
      const errorMessage: any = await response
        .text()
        .catch(() => response.statusText);

      toast.error(`${JSON.parse(errorMessage).msg}`);

      return Promise.reject(
        new Error(
          `HTTP error! status: ${response.status}, message: ${errorMessage}`
        )
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
  options?: RequestOptions
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
  options?: RequestOptions
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
  options?: RequestOptions
) => {
  return request<T>(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(body),
    ...options,
  });
};
