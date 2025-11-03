'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { User } from '@/types/auth'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  error: string | null
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

/**
 * 認証コンテキストプロバイダー
 * アプリケーション全体で認証状態を管理する
 *
 * セキュリティ注意事項:
 * - セッション検証はサーバーサイドで行う必要があります
 * - このコンテキストはクライアントサイドの状態管理のみです
 * - 実際の認可チェックは各APIエンドポイントで実施してください
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  /**
   * セッションの検証とユーザー情報の取得
   * コンポーネントマウント時に実行
   */
  useEffect(() => {
    const verifySession = async () => {
      try {
        const response = await fetch('/api/auth/me', {
          method: 'GET',
          credentials: 'include', // HttpOnly Cookieを含める
        })

        if (response.status === 501) {
          // 認証が未実装の場合はモックユーザーを使用（開発中のみ）
          console.warn(
            '警告: 認証が未実装です。モックユーザーを使用しています。' +
            '本番環境にデプロイする前に必ず実装してください。'
          )
          // TODO: 開発中のみモックユーザーを設定（本番では削除）
          setUser({
            id: '1',
            email: 'user@example.com',
            name: 'テストユーザー',
            role: 'admin',
          })
          setIsLoading(false)
          return
        }

        if (!response.ok) {
          // 認証失敗時はログインページへリダイレクト
          router.push('/login')
          return
        }

        const userData = await response.json()
        setUser(userData)
        setError(null)
      } catch (err) {
        console.error('認証エラー:', err)
        setError('認証に失敗しました')
        // エラー時もログインページへリダイレクト
        router.push('/login')
      } finally {
        setIsLoading(false)
      }
    }

    verifySession()
  }, [router])

  /**
   * ログアウト処理
   * サーバーサイドのセッションを無効化し、ログインページへリダイレクト
   */
  const logout = async () => {
    try {
      setIsLoading(true)

      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      })

      if (!response.ok && response.status !== 501) {
        throw new Error('ログアウトに失敗しました')
      }

      // クライアントサイドの状態をクリア
      setUser(null)
      setError(null)

      // ログインページへリダイレクト
      router.push('/login')
    } catch (err) {
      console.error('ログアウトエラー:', err)
      setError('ログアウトに失敗しました')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, error, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * 認証コンテキストを使用するカスタムフック
 * コンポーネント内で認証状態にアクセスする際に使用
 *
 * @throws {Error} AuthProvider外で使用された場合
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
