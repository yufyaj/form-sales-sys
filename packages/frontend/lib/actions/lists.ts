/**
 * リスト管理のServer Actions
 */

'use server'

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import {
  List,
  ListCreateRequest,
  ListUpdateRequest,
  ListListResponse,
} from '@/lib/api/lists'
import { listSchema, listUpdateSchema } from '@/lib/validations/list'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

/**
 * 認証トークンを取得
 */
async function getAuthToken(): Promise<string | undefined> {
  const cookieStore = await cookies()
  return cookieStore.get('authToken')?.value
}

/**
 * APIエラーハンドリング
 * セキュリティ: サーバーエラーの詳細を隠蔽し、安全なメッセージのみを返す
 */
async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))

    // サーバー側エラー（500番台）は詳細を隠蔽
    if (response.status >= 500) {
      // ログには詳細を記録（サーバー側ログで確認可能）
      console.error('Server error occurred', {
        status: response.status,
        timestamp: new Date().toISOString(),
        // 詳細は含めない（機密情報保護）
      })
      throw new Error(
        'サーバーエラーが発生しました。しばらく経ってから再度お試しください。'
      )
    }

    // クライアントエラー（400番台）は安全なメッセージのみ
    const safeErrorMessages: Record<number, string> = {
      400: '入力内容に誤りがあります',
      401: '認証が必要です',
      403: 'アクセス権限がありません',
      404: 'リソースが見つかりません',
      409: '既に存在するデータです',
      422: '入力内容を確認してください',
    }

    const safeMessage =
      safeErrorMessages[response.status] || 'リクエストの処理に失敗しました'
    throw new Error(safeMessage)
  }

  // 204 No Contentの場合は空のオブジェクトを返す
  if (response.status === 204) {
    return {} as T
  }

  return response.json()
}

/**
 * プロジェクトに紐づくリスト一覧取得
 */
export async function getListsByProject(
  projectId: number,
  skip: number = 0,
  limit: number = 100
): Promise<{ success: boolean; data?: ListListResponse; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/lists?skip=${skip}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // 常に最新データを取得
      }
    )

    const data = await handleApiResponse<ListListResponse>(response)
    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('リスト一覧取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'リスト一覧の取得に失敗しました',
    }
  }
}

/**
 * リスト詳細取得
 */
export async function getListDetail(
  projectId: number,
  listId: number
): Promise<{ success: boolean; data?: List; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/lists/${listId}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      }
    )

    const data = await handleApiResponse<List>(response)
    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('リスト取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'リスト情報の取得に失敗しました',
    }
  }
}

/**
 * リスト作成
 * セキュリティ: サーバーサイドでも入力検証を実施
 */
export async function createListAction(
  projectId: number,
  request: ListCreateRequest
): Promise<{ success: boolean; data?: List; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    // サーバーサイドでの入力検証（多層防御）
    const validationResult = listSchema.safeParse(request)
    if (!validationResult.success) {
      return {
        success: false,
        error: '入力内容に誤りがあります',
      }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/lists`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(validationResult.data),
      }
    )

    const data = await handleApiResponse<List>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/${projectId}/lists`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('リスト作成エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'リストの作成に失敗しました',
    }
  }
}

/**
 * リスト更新
 * セキュリティ: サーバーサイドでも入力検証を実施
 */
export async function updateListAction(
  projectId: number,
  listId: number,
  request: ListUpdateRequest
): Promise<{ success: boolean; data?: List; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    // サーバーサイドでの入力検証（多層防御）
    const validationResult = listUpdateSchema.safeParse(request)
    if (!validationResult.success) {
      return {
        success: false,
        error: '入力内容に誤りがあります',
      }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/lists/${listId}`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(validationResult.data),
      }
    )

    const data = await handleApiResponse<List>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/${projectId}/lists`)
    revalidatePath(`/projects/${projectId}/lists/${listId}/edit`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('リスト更新エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'リスト情報の更新に失敗しました',
    }
  }
}

/**
 * リスト削除
 */
export async function deleteListAction(
  projectId: number,
  listId: number
): Promise<{ success: boolean; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/lists/${listId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    await handleApiResponse<void>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/${projectId}/lists`)

    return { success: true }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('リスト削除エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'リストの削除に失敗しました',
    }
  }
}
