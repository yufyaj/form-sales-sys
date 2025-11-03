'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { UserRole } from '@/types/auth'

interface NavItem {
  label: string
  href: string
  icon: string
  roles?: UserRole[] // このナビゲーション項目を表示できるロール
}

interface SidebarProps {
  userRole?: UserRole
  isMobileMenuOpen?: boolean
  onCloseMobileMenu?: () => void
}

/**
 * サイドバーコンポーネント
 * ロールベースのナビゲーションメニューを提供
 */
export default function Sidebar({
  userRole,
  isMobileMenuOpen = false,
  onCloseMobileMenu
}: SidebarProps) {
  const pathname = usePathname()

  // ナビゲーション項目の定義
  const navItems: NavItem[] = [
    {
      label: 'ダッシュボード',
      href: '/dashboard',
      icon: '📊',
      roles: ['admin', 'manager', 'member'], // 全ロール
    },
    {
      label: 'プロジェクト',
      href: '/projects',
      icon: '📁',
      roles: ['admin', 'manager', 'member'],
    },
    {
      label: 'リスト管理',
      href: '/lists',
      icon: '📋',
      roles: ['admin', 'manager', 'member'],
    },
    {
      label: 'アナリティクス',
      href: '/analytics',
      icon: '📈',
      roles: ['admin', 'manager'],
    },
    {
      label: 'ユーザー管理',
      href: '/users',
      icon: '👥',
      roles: ['admin'], // 管理者のみ
    },
    {
      label: '設定',
      href: '/settings',
      icon: '⚙️',
      roles: ['admin', 'manager', 'member'],
    },
  ]

  // ロールに基づいてナビゲーション項目をフィルタリング
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
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onCloseMobileMenu}
          aria-hidden="true"
        />
      )}

      {/* サイドバー */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 transform border-r border-gray-200 bg-white transition-transform duration-200 ease-in-out
          lg:static lg:transform-none
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <nav className="flex h-full flex-col px-4 py-6">
          {/* ナビゲーション項目 */}
          <ul className="flex-1 space-y-1">
            {filteredNavItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  onClick={onCloseMobileMenu}
                  className={`
                    flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors
                    ${
                      isActive(item.href)
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <span className="text-xl" aria-hidden="true">
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>

          {/* フッター情報 */}
          {userRole && (
            <div className="mt-auto border-t border-gray-200 pt-4">
              <p className="px-4 text-xs text-gray-500">
                ロール: {getRoleLabel(userRole)}
              </p>
            </div>
          )}
        </nav>
      </aside>
    </>
  )
}

/**
 * ロールのラベルを取得
 */
function getRoleLabel(role: UserRole): string {
  const roleLabels: Record<UserRole, string> = {
    admin: '管理者',
    manager: 'マネージャー',
    member: 'メンバー',
  }
  return roleLabels[role]
}
