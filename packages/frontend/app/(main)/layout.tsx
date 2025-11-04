'use client'

import { useAuth } from '@/contexts/AuthContext'
import MainLayout from '@/components/common/MainLayout'

/**
 * メインレイアウトグループ
 * 認証後のページで共有されるレイアウト
 *
 * セキュリティ改善点:
 * - AuthContextを使用してセッション検証を実施
 * - 認証されていない場合はログインページへリダイレクト
 * - ログアウト処理を適切に実装
 *
 * TODO（本番環境デプロイ前に必須）:
 * - /api/auth/meエンドポイントの完全実装
 * - /api/auth/logoutエンドポイントの完全実装
 * - セッション管理の実装（HttpOnly Cookie使用）
 * - CSRF対策の実装
 */
export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, isLoading, error, logout } = useAuth()

  // ローディング中の表示
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  // エラー発生時の表示
  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mb-4 text-6xl">⚠️</div>
          <h1 className="mb-2 text-2xl font-bold text-gray-900">
            認証エラー
          </h1>
          <p className="mb-6 text-gray-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="rounded-lg bg-blue-600 px-6 py-3 text-white transition-colors hover:bg-blue-700"
          >
            再読み込み
          </button>
        </div>
      </div>
    )
  }

  // 認証されていない場合は何も表示しない（リダイレクト中）
  if (!user) {
    return null
  }

  return (
    <MainLayout user={user} onLogout={logout}>
      {children}
    </MainLayout>
  )
}
