'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  FolderKanban,
  List,
  BarChart3,
  Users,
  Settings,
  LucideIcon,
} from 'lucide-react'
import { UserRole } from '@/types/auth'
import { slideInLeft, staggerContainer, staggerItem } from '@/lib/motion'

interface NavItem {
  label: string
  href: string
  icon: LucideIcon
  roles?: UserRole[] // このナビゲーション項目を表示できるロール
}

interface SidebarProps {
  userRole?: UserRole
  isMobileMenuOpen?: boolean
  onCloseMobileMenu?: () => void
}

/**
 * モダンなサイドバーコンポーネント
 * グラスモーフィズム効果とスムーズなアニメーション
 */
export default function Sidebar({
  userRole,
  isMobileMenuOpen = false,
  onCloseMobileMenu
}: SidebarProps) {
  const pathname = usePathname()
  const MotionDiv = motion.div as any
  const MotionAside = motion.aside as any
  const MotionLink = motion(Link) as any

  // ナビゲーション項目の定義
  const navItems: NavItem[] = [
    {
      label: 'ダッシュボード',
      href: '/dashboard',
      icon: LayoutDashboard,
      roles: ['sales_company', 'customer', 'worker'], // 全ロール
    },
    {
      label: 'プロジェクト',
      href: '/projects',
      icon: FolderKanban,
      roles: ['sales_company', 'customer'],
    },
    {
      label: 'リスト管理',
      href: '/lists',
      icon: List,
      roles: ['sales_company', 'customer'],
    },
    {
      label: 'アナリティクス',
      href: '/analytics',
      icon: BarChart3,
      roles: ['sales_company'],
    },
    {
      label: 'ユーザー管理',
      href: '/users',
      icon: Users,
      roles: ['sales_company'], // 営業支援会社のみ
    },
    {
      label: '設定',
      href: '/settings',
      icon: Settings,
      roles: ['sales_company', 'customer', 'worker'],
    },
  ]

  /**
   * ロールに基づいてナビゲーション項目をフィルタリング
   *
   * 重要なセキュリティ注意事項:
   * このフィルタリングはUX向けの表示制御のみです。
   * 実際の認可チェックは必ずサーバーサイドで実施してください。
   * クライアントサイドのJavaScriptは改変可能であり、
   * UIを非表示にするだけではセキュリティ対策として不十分です。
   */
  const filteredNavItems = navItems.filter(item => {
    if (!item.roles) return true
    if (!userRole) return false
    return item.roles.includes(userRole)
  })

  const isActive = (href: string) => pathname === href || pathname?.startsWith(href + '/')

  return (
    <>
      {/* モバイルメニュー用のオーバーレイ */}
      {isMobileMenuOpen && (
        <MotionDiv
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={onCloseMobileMenu}
          aria-hidden="true"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        />
      )}

      {/* サイドバー */}
      <MotionAside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 glass border-r border-neutral-200/50 dark:border-neutral-800/50
          transform transition-transform duration-base ease-in-out
          lg:static lg:transform-none
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
        initial="hidden"
        animate="visible"
        variants={slideInLeft}
      >
        <nav className="flex h-full flex-col px-4 py-6">
          {/* ロゴ・ブランディング */}
          <MotionDiv
            className="mb-8 px-4"
            variants={staggerItem}
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 shadow-md">
                <LayoutDashboard className="h-5 w-5 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                  Form Sales
                </span>
                <span className="text-xs text-neutral-500 dark:text-neutral-400">
                  Support System
                </span>
              </div>
            </div>
          </MotionDiv>

          {/* ナビゲーション項目 */}
          <MotionDiv
            className="flex-1 space-y-1"
            variants={staggerContainer}
          >
            {filteredNavItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)

              return (
                <MotionDiv
                  key={item.href}
                  variants={staggerItem}
                >
                  <MotionLink
                    href={item.href}
                    onClick={onCloseMobileMenu}
                    className={`
                      group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium
                      transition-all duration-base
                      ${
                        active
                          ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-md'
                          : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100/80 dark:hover:bg-neutral-800/80'
                      }
                    `}
                    whileHover={{ x: active ? 0 : 4 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Icon
                      className={`h-5 w-5 ${
                        active
                          ? 'text-white'
                          : 'text-neutral-500 dark:text-neutral-400 group-hover:text-neutral-700 dark:group-hover:text-neutral-200'
                      }`}
                    />
                    <span>{item.label}</span>
                    {active && (
                      <MotionDiv
                        className="ml-auto h-1.5 w-1.5 rounded-full bg-white"
                        layoutId="active-indicator"
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.2 }}
                      />
                    )}
                  </MotionLink>
                </MotionDiv>
              )
            })}
          </MotionDiv>

          {/* フッター情報 */}
          {userRole && (
            <MotionDiv
              className="mt-auto border-t border-neutral-200/50 dark:border-neutral-800/50 pt-4"
              variants={staggerItem}
            >
              <div className="px-4 py-2 rounded-lg bg-neutral-100/50 dark:bg-neutral-800/50">
                <p className="text-xs font-medium text-neutral-600 dark:text-neutral-400">
                  ログイン中
                </p>
                <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-0.5">
                  {getRoleLabel(userRole)}
                </p>
              </div>
            </MotionDiv>
          )}
        </nav>
      </MotionAside>
    </>
  )
}

/**
 * ロールのラベルを取得
 */
function getRoleLabel(role: UserRole): string {
  const roleLabels: Record<UserRole, string> = {
    sales_company: '営業支援会社',
    customer: '顧客',
    worker: 'ワーカー',
  }
  return roleLabels[role]
}
