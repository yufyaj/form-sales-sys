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
  email: string;
  name?: string;
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
