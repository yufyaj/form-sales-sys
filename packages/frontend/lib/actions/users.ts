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
 */
async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `APIエラー: ${response.status}`)
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
    console.error('ユーザー一覧取得エラー:', error)
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
    console.error('ユーザー取得エラー:', error)
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
    console.error('ユーザー・ロール取得エラー:', error)
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
    console.error('ユーザー作成エラー:', error)
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
    console.error('ユーザー更新エラー:', error)
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
    console.error('ユーザー削除エラー:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'ユーザーの削除に失敗しました',
    }
  }
}
