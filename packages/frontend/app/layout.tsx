import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'フォーム営業支援システム',
  description: 'フォーム営業活動を効率化するための支援システム',
}

/**
 * ルートレイアウト
 * すべてのページで共有されるレイアウト
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-gray-50 antialiased">{children}</body>
    </html>
  )
}
