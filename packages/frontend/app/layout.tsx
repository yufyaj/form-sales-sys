import type { Metadata } from 'next'
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
 * - サーバーコンポーネントとして実装し、Hydration問題を回避
 */
export const metadata: Metadata = {
  title: 'フォーム営業支援システム',
  description: '営業支援会社向けのフォーム営業支援システム',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body className="min-h-screen bg-gray-50 antialiased">
        <ErrorBoundary>
          <AuthProvider>{children}</AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
