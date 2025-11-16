/**
 * ユーザー関連の型定義
 */

/**
 * ユーザー基本情報
 */
export interface User {
  id: number
  organization_id: number
  email: string
  full_name: string
  phone: string | null
  avatar_url: string | null
  description: string | null
  is_active: boolean
  is_email_verified: boolean
  created_at: string
  updated_at: string
  deleted_at: string | null
}

/**
 * ロール情報
 */
export interface Role {
  id: number
  name: string
  display_name: string
  description: string | null
}

/**
 * ロールを含むユーザー情報
 */
export interface UserWithRoles extends User {
  roles: Role[]
}

/**
 * ユーザー一覧レスポンス
 */
export interface UserListResponse {
  users: User[]
  total: number
  skip: number
  limit: number
}

/**
 * ユーザー作成リクエスト
 */
export interface UserCreateRequest {
  organization_id: number
  email: string
  full_name: string
  password: string
  phone?: string | null
  description?: string | null
}

/**
 * ユーザー更新リクエスト
 */
export interface UserUpdateRequest {
  email?: string
  full_name?: string
  phone?: string | null
  avatar_url?: string | null
  description?: string | null
  is_active?: boolean
}

/**
 * パスワード変更リクエスト
 */
export interface PasswordChangeRequest {
  old_password: string
  new_password: string
}

/**
 * ロール割り当てリクエスト
 */
export interface RoleAssignRequest {
  role_id: number
}
