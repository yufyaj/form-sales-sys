'use client'

import './globals.css'
import { AuthProvider } from '@/contexts/AuthContext'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'

/**
 * ルートレイアウト
 * すべてのページで共有されるレイアウト
 *
 * セキュリティ改善点:
 * - ErrorBoundaryで予期しないエラーをキャッチ
 * - AuthProviderでアプリケーション全体の認証状態を管理
 * - クライアントコンポーネントとして実装（AuthContextが必要なため）
 *
 * 注意: metadataはクライアントコンポーネントでは使用できないため、
 * 各ページで個別にメタデータを設定してください
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-gray-50 antialiased">
        <ErrorBoundary>
          <AuthProvider>{children}</AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
