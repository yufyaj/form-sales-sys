'use client'

import { useState } from 'react'
import { User } from '@/types/auth'
import Header from './Header'
import Sidebar from './Sidebar'

interface MainLayoutProps {
  children: React.ReactNode
  user?: User
  onLogout?: () => void
}

/**
 * メインレイアウトコンポーネント
 * ヘッダー、サイドバー、メインコンテンツエリアを含むレイアウト
 * レスポンシブデザイン対応
 */
export default function MainLayout({ children, user, onLogout }: MainLayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* サイドバー */}
      <Sidebar
        userRole={user?.role}
        isMobileMenuOpen={isMobileMenuOpen}
        onCloseMobileMenu={() => setIsMobileMenuOpen(false)}
      />

      {/* メインコンテンツエリア */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* ヘッダー */}
        <div className="relative">
          {/* モバイルメニューボタン */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="absolute left-4 top-4 z-50 rounded-lg p-2 text-gray-600 hover:bg-gray-100 lg:hidden"
            aria-label="メニューを開く"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>

          <Header user={user} onLogout={onLogout} />
        </div>

        {/* メインコンテンツ */}
        <main className="flex-1 overflow-y-auto">
          <div className="h-full">{children}</div>
        </main>
      </div>
    </div>
  )
}
