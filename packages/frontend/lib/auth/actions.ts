'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import type { LoginFormData, ResetPasswordFormData } from '@/lib/validations/auth'

/**
 * ログイン処理（Server Action）
 * httpOnlyクッキーを使用してトークンを安全に保存
 */
export async function loginAction(formData: LoginFormData) {
  try {
    // バックエンドAPIにログインリクエストを送信
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: 'ネットワークエラーが発生しました',
      }))
      return {
        success: false,
        error: error.message || '認証に失敗しました',
      }
    }

    const data = await response.json()

    // httpOnlyクッキーとしてトークンを保存
    // これによりJavaScriptからアクセスできなくなり、XSS攻撃を防ぐ
    const cookieStore = await cookies()
    cookieStore.set('authToken', data.access_token, {
      httpOnly: true, // JavaScriptからアクセス不可
      secure: process.env.NODE_ENV === 'production', // HTTPS環境でのみ送信
      sameSite: 'lax', // CSRF対策
      maxAge: 60 * 60 * 24 * 7, // 7日間
      path: '/',
    })

    return {
      success: true,
    }
  } catch (error) {
    console.error('Login error:', error)
    return {
      success: false,
      error: '予期しないエラーが発生しました',
    }
  }
}

/**
 * ログアウト処理（Server Action）
 */
export async function logoutAction() {
  try {
    const cookieStore = await cookies()

    // 認証クッキーを削除
    cookieStore.delete('authToken')
    cookieStore.delete('user')

    return {
      success: true,
    }
  } catch (error) {
    console.error('Logout error:', error)
    return {
      success: false,
      error: 'ログアウトに失敗しました',
    }
  }
}

/**
 * パスワードリセットリクエスト（Server Action）
 */
export async function requestPasswordResetAction(formData: ResetPasswordFormData) {
  try {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    const response = await fetch(`${API_BASE_URL}/auth/password-reset-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: 'ネットワークエラーが発生しました',
      }))
      return {
        success: false,
        error: error.message || 'リクエストに失敗しました',
      }
    }

    const data = await response.json()

    return {
      success: true,
      message: data.message || 'パスワードリセットリンクをメールで送信しました。',
    }
  } catch (error) {
    console.error('Password reset error:', error)
    return {
      success: false,
      error: '予期しないエラーが発生しました',
    }
  }
}

/**
 * 認証状態のチェック
 */
export async function checkAuth() {
  try {
    const cookieStore = await cookies()
    const authToken = cookieStore.get('authToken')
    const userCookie = cookieStore.get('user')

    if (!authToken || !userCookie) {
      return {
        isAuthenticated: false,
        user: null,
      }
    }

    return {
      isAuthenticated: true,
      user: JSON.parse(userCookie.value),
    }
  } catch (error) {
    console.error('Check auth error:', error)
    return {
      isAuthenticated: false,
      user: null,
    }
  }
}
