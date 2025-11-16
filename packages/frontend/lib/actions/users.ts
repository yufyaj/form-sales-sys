/**
 * ユーザー管理のServer Actions
 */

'use server'

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import {
  User,
  UserCreateRequest,
  UserListResponse,
  UserUpdateRequest,
  UserWithRoles,
} from '@/types/user'

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
 * ユーザー一覧取得
 */
export async function getUserList(
  organizationId: number,
  skip: number = 0,
  limit: number = 100
): Promise<{ success: boolean; data?: UserListResponse; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/users?organization_id=${organizationId}&skip=${skip}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // 常に最新データを取得
      }
    )

    const data = await handleApiResponse<UserListResponse>(response)
    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('ユーザー一覧取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
      // トークンやパラメータは含めない
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'ユーザー一覧の取得に失敗しました',
    }
  }
}

/**
 * ユーザー詳細取得
 */
export async function getUser(
  userId: number,
  organizationId: number
): Promise<{ success: boolean; data?: User; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/users/${userId}?organization_id=${organizationId}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      }
    )

    const data = await handleApiResponse<User>(response)
    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('ユーザー取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'ユーザー情報の取得に失敗しました',
    }
  }
}

/**
 * ユーザーとロール取得
 */
export async function getUserWithRoles(
  userId: number,
  organizationId: number
): Promise<{ success: boolean; data?: UserWithRoles; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/users/${userId}/roles?organization_id=${organizationId}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      }
    )

    const data = await handleApiResponse<UserWithRoles>(response)
    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('ユーザー・ロール取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'ユーザー情報の取得に失敗しました',
    }
  }
}

/**
 * ユーザー作成
 */
export async function createUser(
  request: UserCreateRequest
): Promise<{ success: boolean; data?: User; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    const data = await handleApiResponse<User>(response)

    // キャッシュ再検証
    revalidatePath('/dashboard/sales-company/staff')

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('ユーザー作成エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'ユーザーの作成に失敗しました',
    }
  }
}

/**
 * ユーザー更新
 */
export async function updateUser(
  userId: number,
  organizationId: number,
  request: UserUpdateRequest
): Promise<{ success: boolean; data?: User; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/users/${userId}?organization_id=${organizationId}`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    )

    const data = await handleApiResponse<User>(response)

    // キャッシュ再検証
    revalidatePath('/dashboard/sales-company/staff')

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('ユーザー更新エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'ユーザー情報の更新に失敗しました',
    }
  }
}

/**
 * ユーザー削除
 */
export async function deleteUser(
  userId: number,
  organizationId: number
): Promise<{ success: boolean; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/users/${userId}?organization_id=${organizationId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    await handleApiResponse<void>(response)

    // キャッシュ再検証
    revalidatePath('/dashboard/sales-company/staff')

    return { success: true }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('ユーザー削除エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : 'ユーザーの削除に失敗しました',
    }
  }
}
