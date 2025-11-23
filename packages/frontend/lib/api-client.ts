import { getOrCreateCSRFToken } from './csrf'
import { env } from './env'

/**
 * APIエラー
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * API リクエストオプション
 */
interface ApiRequestOptions extends RequestInit {
  requireAuth?: boolean // 認証が必要か（デフォルト: true）
}

/**
 * APIベースURL
 * 検証済みの環境変数から取得、デフォルトはローカル開発用
 */
const API_BASE_URL = env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * 安全なAPIリクエストを実行
 *
 * セキュリティ機能:
 * - CSRFトークンの自動付与（POST/PUT/DELETE/PATCHリクエスト）
 * - エラーハンドリングの統一
 * - 認証エラー時の自動リダイレクト
 * - レスポンスの型安全性
 *
 * @param url - APIエンドポイントのパス（/api/...）
 * @param options - リクエストオプション
 * @returns レスポンスデータ
 */
export async function apiRequest<T>(
  url: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const { requireAuth = true, ...fetchOptions } = options

  // デフォルトのヘッダー
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  // 既存のヘッダーをマージ
  if (fetchOptions.headers) {
    const existingHeaders = fetchOptions.headers as Record<string, string>
    Object.assign(headers, existingHeaders)
  }

  // CSRF対策: POST/PUT/DELETE/PATCHリクエストにCSRFトークンを付与
  const method = fetchOptions.method?.toUpperCase() || 'GET'
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
    const csrfToken = getOrCreateCSRFToken()
    if (csrfToken) {
      headers['X-CSRF-Token'] = csrfToken
    }
  }

  // フルURLを構築
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`

  try {
    const response = await fetch(fullUrl, {
      ...fetchOptions,
      credentials: 'include', // HttpOnly Cookieを送信
      headers,
    })

    // エラーレスポンスの処理
    if (!response.ok) {
      // 401 Unauthorized: 認証エラー
      if (response.status === 401 && requireAuth) {
        // ログインページへリダイレクト
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        throw new ApiError('Unauthorized', 401)
      }

      // 403 Forbidden: 権限エラー
      if (response.status === 403) {
        throw new ApiError('Forbidden: You do not have permission to access this resource', 403)
      }

      // 404 Not Found
      if (response.status === 404) {
        throw new ApiError('Resource not found', 404)
      }

      // その他のエラー
      let errorData: unknown
      try {
        errorData = await response.json()
      } catch {
        errorData = await response.text()
      }

      throw new ApiError(
        `API Error: ${response.status} ${response.statusText}`,
        response.status,
        errorData
      )
    }

    // 成功レスポンスのパース
    // 204 No Contentの場合は空オブジェクトを返す
    if (response.status === 204) {
      return {} as T
    }

    const data = await response.json()
    return data as T
  } catch (error) {
    // ApiErrorはそのまま再スロー
    if (error instanceof ApiError) {
      throw error
    }

    // その他のエラー（ネットワークエラー等）
    if (error instanceof Error) {
      throw new ApiError(`Network Error: ${error.message}`, 0)
    }

    throw new ApiError('Unknown error occurred', 0)
  }
}

/**
 * GETリクエストのヘルパー
 */
export async function get<T>(url: string, options?: ApiRequestOptions): Promise<T> {
  return apiRequest<T>(url, { ...options, method: 'GET' })
}

/**
 * POSTリクエストのヘルパー
 */
export async function post<T>(
  url: string,
  data?: unknown,
  options?: ApiRequestOptions
): Promise<T> {
  return apiRequest<T>(url, {
    ...options,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * PUTリクエストのヘルパー
 */
export async function put<T>(
  url: string,
  data?: unknown,
  options?: ApiRequestOptions
): Promise<T> {
  return apiRequest<T>(url, {
    ...options,
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * PATCHリクエストのヘルパー
 */
export async function patch<T>(
  url: string,
  data?: unknown,
  options?: ApiRequestOptions
): Promise<T> {
  return apiRequest<T>(url, {
    ...options,
    method: 'PATCH',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * DELETEリクエストのヘルパー
 */
export async function del<T>(url: string, options?: ApiRequestOptions): Promise<T> {
  return apiRequest<T>(url, { ...options, method: 'DELETE' })
}
