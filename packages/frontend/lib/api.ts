import type { LoginFormData, AuthResponse, ApiError } from '@/types/auth'

/**
 * APIクライアント
 * バックエンドとの通信を担当
 * CSRF対策とHTTPS強制を実装
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * API URLの妥当性を検証
 */
function validateApiUrl(url: string): void {
  try {
    const parsed = new URL(url)

    // 許可されたプロトコルのみ
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      throw new Error(`不正なプロトコル: ${parsed.protocol}`)
    }

    // 本番環境ではHTTPSを強制
    if (process.env.NODE_ENV === 'production' && parsed.protocol !== 'https:') {
      throw new Error('本番環境ではHTTPSを使用する必要があります')
    }

    // 本番環境では許可されたホストのみアクセス可能
    if (process.env.NODE_ENV === 'production') {
      const allowedHosts = process.env.NEXT_PUBLIC_ALLOWED_API_HOSTS?.split(',') || []
      if (allowedHosts.length > 0 && !allowedHosts.includes(parsed.hostname)) {
        throw new Error(`許可されていないホスト: ${parsed.hostname}`)
      }
    }
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(`無効なURL形式: ${url}`)
    }
    throw error
  }
}

// URL検証を実行
if (typeof window !== 'undefined') {
  validateApiUrl(API_BASE_URL)
}

/**
 * CSRFトークンのキャッシュ
 */
let csrfTokenCache: { token: string | null; timestamp: number } = {
  token: null,
  timestamp: 0,
}

const CSRF_TOKEN_CACHE_DURATION = 5 * 60 * 1000 // 5分

/**
 * CSRFトークンを取得（キャッシュ機能付き）
 */
function getCsrfToken(): string | null {
  if (typeof document === 'undefined') return null

  const now = Date.now()

  // キャッシュが有効な場合は再利用
  if (
    csrfTokenCache.token &&
    now - csrfTokenCache.timestamp < CSRF_TOKEN_CACHE_DURATION
  ) {
    return csrfTokenCache.token
  }

  // メタタグからCSRFトークンを取得
  const csrfMeta = document.querySelector('meta[name="csrf-token"]')
  if (csrfMeta) {
    const token = csrfMeta.getAttribute('content')
    csrfTokenCache = { token, timestamp: now }
    return token
  }

  // クッキーからCSRFトークンを取得（フォールバック）
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'XSRF-TOKEN') {
      const token = decodeURIComponent(value)
      csrfTokenCache = { token, timestamp: now }
      return token
    }
  }

  csrfTokenCache = { token: null, timestamp: 0 }
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

        // 本番環境では一般的なエラーメッセージを使用
        const userMessage =
          process.env.NODE_ENV === 'production'
            ? 'リクエストの処理中にエラーが発生しました'
            : error.message

        // 開発環境でのみ詳細をログ出力
        if (process.env.NODE_ENV === 'development') {
          console.error('API Error Details:', {
            status: response.status,
            statusText: response.statusText,
            error,
          })
        }

        throw new Error(userMessage)
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
