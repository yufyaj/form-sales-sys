import type { LoginFormData, AuthResponse, ApiError } from '@/types/auth'

/**
 * APIクライアント
 * バックエンドとの通信を担当
 * CSRF対策とHTTPS強制を実装
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// 本番環境ではHTTPSを強制
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'production' && !API_BASE_URL.startsWith('https://')) {
  throw new Error('本番環境ではHTTPSを使用する必要があります')
}

/**
 * CSRFトークンを取得
 */
function getCsrfToken(): string | null {
  if (typeof document === 'undefined') return null

  // メタタグからCSRFトークンを取得
  const csrfMeta = document.querySelector('meta[name="csrf-token"]')
  if (csrfMeta) {
    return csrfMeta.getAttribute('content')
  }

  // クッキーからCSRFトークンを取得（フォールバック）
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'XSRF-TOKEN') {
      return decodeURIComponent(value)
    }
  }

  return null
}

class ApiClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  /**
   * 共通のfetchラッパー
   * エラーハンドリングとレスポンス変換を一元管理
   * CSRF対策を実装
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    try {
      // ヘッダーを構築
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
      }

      // POST/PUT/DELETE/PATCHリクエストにCSRFトークンを追加
      if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method || 'GET')) {
        const csrfToken = getCsrfToken()
        if (csrfToken) {
          headers['X-CSRF-Token'] = csrfToken
        }
      }

      const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include', // クッキーを含める（CSRF対策とセッション管理）
      })

      // レスポンスが正常でない場合はエラーをスロー
      if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({
          message: 'ネットワークエラーが発生しました',
        }))
        throw new Error(error.message)
      }

      return response.json()
    } catch (error) {
      // ネットワークエラーなどのハンドリング
      if (error instanceof Error) {
        throw error
      }
      throw new Error('予期しないエラーが発生しました')
    }
  }

  /**
   * ログインAPI
   */
  async login(data: LoginFormData): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  /**
   * パスワードリセットリクエストAPI
   */
  async requestPasswordReset(email: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('/auth/password-reset-request', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  }

  /**
   * GETリクエスト
   */
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'GET',
    })
  }

  /**
   * POSTリクエスト
   */
  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * PUTリクエスト
   */
  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * PATCHリクエスト
   */
  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * DELETEリクエスト
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    })
  }
}

export const apiClient = new ApiClient(API_BASE_URL)

// 便利な関数エクスポート
export const get = <T>(endpoint: string) => apiClient.get<T>(endpoint)
export const post = <T>(endpoint: string, data?: unknown) =>
  apiClient.post<T>(endpoint, data)
export const put = <T>(endpoint: string, data?: unknown) =>
  apiClient.put<T>(endpoint, data)
export const patch = <T>(endpoint: string, data?: unknown) =>
  apiClient.patch<T>(endpoint, data)
export const del = <T>(endpoint: string) => apiClient.delete<T>(endpoint)
