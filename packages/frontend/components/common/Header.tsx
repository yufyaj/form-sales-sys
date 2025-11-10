'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { User as UserIcon, ChevronDown, LogOut, Settings } from 'lucide-react'
import { User, UserRole, sanitizeUserName } from '@/types/auth'
import { fadeInDown, staggerContainer, staggerItem } from '@/lib/motion'

interface HeaderProps {
  user?: User
  onLogout?: () => void
}

/**
 * モダンなヘッダーコンポーネント
 * グラスモーフィズム効果とスムーズなアニメーション
 */
export default function Header({ user, onLogout }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const MotionDiv = motion.div as any

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
    <MotionDiv
      className="sticky top-0 z-40 w-full glass border-b border-neutral-200/50 dark:border-neutral-800/50"
      initial="hidden"
      animate="visible"
      variants={fadeInDown}
    >
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* ロゴ・タイトル */}
        <MotionDiv
          className="flex items-center gap-4"
          variants={staggerItem}
        >
          <h1 className="text-xl font-bold bg-gradient-to-r from-neutral-900 to-neutral-600 dark:from-neutral-100 dark:to-neutral-400 bg-clip-text text-transparent">
            フォーム営業支援システム
          </h1>
        </MotionDiv>

        {/* ユーザーメニュー */}
        {user && (
          <MotionDiv
            className="relative"
            variants={staggerItem}
          >
            <motion.button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/80 transition-colors duration-base"
              aria-label="ユーザーメニュー"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-md">
                {displayName?.charAt(0).toUpperCase()}
              </div>
              <span className="hidden sm:inline">{displayName}</span>
              <ChevronDown
                className={`h-4 w-4 transition-transform duration-base ${
                  isMenuOpen ? 'rotate-180' : ''
                }`}
              />
            </motion.button>

            {/* ドロップダウンメニュー */}
            <AnimatePresence>
              {isMenuOpen && (
                <>
                  <MotionDiv
                    className="fixed inset-0 z-10"
                    onClick={() => setIsMenuOpen(false)}
                    aria-hidden="true"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                  />
                  <MotionDiv
                    className="absolute right-0 z-20 mt-2 w-56 rounded-xl border border-neutral-200/50 dark:border-neutral-800/50 glass-strong shadow-xl overflow-hidden"
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    variants={staggerContainer}
                  >
                    {/* ユーザー情報 */}
                    <MotionDiv
                      className="p-4 border-b border-neutral-200/50 dark:border-neutral-800/50"
                      variants={staggerItem}
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-md">
                          {displayName?.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate">
                            {displayName}
                          </p>
                          <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">
                            {user.email}
                          </p>
                        </div>
                      </div>
                      {user.role && (
                        <div className="mt-2">
                          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300">
                            {getRoleLabel(user.role)}
                          </span>
                        </div>
                      )}
                    </MotionDiv>

                    {/* メニュー項目 */}
                    <div className="p-2">
                      <MotionDiv variants={staggerItem}>
                        <button
                          onClick={() => {
                            setIsMenuOpen(false)
                            // TODO: 設定ページへの遷移
                          }}
                          className="w-full flex items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/80 transition-colors duration-base"
                        >
                          <Settings className="h-4 w-4" />
                          設定
                        </button>
                      </MotionDiv>
                      <MotionDiv variants={staggerItem}>
                        <button
                          onClick={() => {
                            setIsMenuOpen(false)
                            onLogout?.()
                          }}
                          className="w-full flex items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/50 transition-colors duration-base"
                        >
                          <LogOut className="h-4 w-4" />
                          ログアウト
                        </button>
                      </MotionDiv>
                    </div>
                  </MotionDiv>
                </>
              )}
            </AnimatePresence>
          </MotionDiv>
        )}
      </div>
    </MotionDiv>
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
