/**
 * 認証関連の型定義
 */

export interface LoginFormData {
  email: string;
  password: string;
}

export interface ResetPasswordFormData {
  email: string;
}

/**
 * ユーザーロール
 */
export type UserRole = 'admin' | 'manager' | 'member';

export interface User {
  id: string;
  email: string; // サーバー側でメールアドレス形式をバリデーション必須
  name?: string; // 最大長制限、特殊文字制限を設ける
  role?: UserRole;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface ApiError {
  message: string;
  code?: string;
}

/**
 * ユーザー名をサニタイズする
 * XSS対策として制御文字を削除し、最大長を制限する
 *
 * @param name - サニタイズするユーザー名
 * @returns サニタイズされたユーザー名、またはundefined
 */
export function sanitizeUserName(name: string | undefined): string | undefined {
  if (!name) return undefined

  // 最大長制限（50文字）
  const truncated = name.slice(0, 50)

  // 制御文字を削除（XSS対策の追加レイヤー）
  const cleaned = truncated.replace(/[\x00-\x1F\x7F-\x9F]/g, '')

  return cleaned || undefined
}
