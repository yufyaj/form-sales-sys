'use client'

import { useState, useEffect } from 'react'
import { User, UserRole, sanitizeUserName } from '@/types/auth'

interface HeaderProps {
  user?: User
  onLogout?: () => void
}

/**
 * ヘッダーコンポーネント
 * ユーザー情報の表示とログアウト機能を提供
 */
export default function Header({ user, onLogout }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  // Escapeキーでメニューを閉じる（アクセシビリティ向上）
  useEffect(() => {
    if (!isMenuOpen) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsMenuOpen(false)
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isMenuOpen])

  // サニタイズされた表示名を取得（XSS対策）
  const displayName = sanitizeUserName(user?.name) || user?.email

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* ロゴ・タイトル */}
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-gray-900">
            フォーム営業支援システム
          </h1>
        </div>

        {/* ユーザーメニュー */}
        {user && (
          <div className="relative">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
              aria-label="ユーザーメニュー"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white">
                {displayName?.charAt(0).toUpperCase()}
              </div>
              <span className="hidden sm:inline">{displayName}</span>
              <svg
                className={`h-4 w-4 transition-transform ${isMenuOpen ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {/* ドロップダウンメニュー */}
            {isMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setIsMenuOpen(false)}
                  aria-hidden="true"
                />
                <div className="absolute right-0 z-20 mt-2 w-48 rounded-lg border border-gray-200 bg-white shadow-lg">
                  <div className="p-3 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">
                      {displayName}
                    </p>
                    <p className="text-xs text-gray-500">{user.email}</p>
                    {user.role && (
                      <p className="mt-1 text-xs text-gray-500">
                        ロール: {getRoleLabel(user.role)}
                      </p>
                    )}
                  </div>
                  <div className="p-1">
                    <button
                      onClick={() => {
                        setIsMenuOpen(false)
                        onLogout?.()
                      }}
                      className="w-full rounded px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50"
                    >
                      ログアウト
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </header>
  )
}

/**
 * ロールのラベルを取得（型安全性向上）
 */
function getRoleLabel(role: UserRole): string {
  const roleLabels: Record<UserRole, string> = {
    sales_company: '営業支援会社',
    customer: '顧客',
    worker: 'ワーカー',
  }
  return roleLabels[role]
}
