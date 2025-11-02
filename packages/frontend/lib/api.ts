import type { LoginFormData, AuthResponse, ApiError } from '@/types/auth'

/**
 * APIクライアント
 * バックエンドとの通信を担当
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  /**
   * 共通のfetchラッパー
   * エラーハンドリングとレスポンス変換を一元管理
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
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
    return this.request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  /**
   * パスワードリセットリクエストAPI
   */
  async requestPasswordReset(email: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
