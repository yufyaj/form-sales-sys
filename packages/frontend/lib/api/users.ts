/**
 * ユーザーAPI
 */

import { get, post, patch, del } from '@/lib/api-client'
import type {
  User,
  UserListResponse,
  UserCreateRequest,
  UserUpdateRequest,
} from '@/types/user'

/**
 * ユーザー一覧取得のパラメータ
 */
export interface UserListParams {
  skip?: number
  limit?: number
  role?: string // ロールでフィルタ（例: 'worker', 'sales_company_staff'）
  is_active?: boolean // アクティブユーザーのみ取得
}

/**
 * ユーザー一覧を取得
 */
export async function listUsers(
  params?: UserListParams
): Promise<UserListResponse> {
  const searchParams = new URLSearchParams()

  if (params?.skip !== undefined) {
    searchParams.append('skip', params.skip.toString())
  }
  if (params?.limit !== undefined) {
    searchParams.append('limit', params.limit.toString())
  }
  if (params?.role) {
    searchParams.append('role', params.role)
  }
  if (params?.is_active !== undefined) {
    searchParams.append('is_active', params.is_active.toString())
  }

  const url = `/api/v1/users${
    searchParams.toString() ? `?${searchParams.toString()}` : ''
  }`
  return get<UserListResponse>(url)
}

/**
 * ワーカー一覧を取得（アクティブなワーカーのみ）
 */
export async function listWorkers(
  params?: Omit<UserListParams, 'role'>
): Promise<UserListResponse> {
  return listUsers({
    ...params,
    role: 'worker',
    is_active: true,
  })
}

/**
 * ユーザー詳細を取得
 */
export async function getUser(userId: number): Promise<User> {
  return get<User>(`/api/v1/users/${userId}`)
}

/**
 * ユーザーを作成
 */
export async function createUser(data: UserCreateRequest): Promise<User> {
  return post<User>('/api/v1/users', data)
}

/**
 * ユーザーを更新
 */
export async function updateUser(
  userId: number,
  data: UserUpdateRequest
): Promise<User> {
  return patch<User>(`/api/v1/users/${userId}`, data)
}

/**
 * ユーザーを削除
 */
export async function deleteUser(userId: number): Promise<void> {
  return del<void>(`/api/v1/users/${userId}`)
}
