'use client'

import MainLayout from '@/components/common/MainLayout'

/**
 * メインレイアウトグループ
 * 認証後のページで共有されるレイアウト
 * TODO: 認証チェックとセッション管理を実装
 */
export default function Layout({ children }: { children: React.ReactNode }) {
  // TODO: 実際の認証状態とユーザー情報を取得
  // 現在はダミーデータを使用
  const mockUser = {
    id: '1',
    email: 'user@example.com',
    name: 'テストユーザー',
    role: 'admin' as const,
  }

  const handleLogout = () => {
    // TODO: ログアウト処理を実装
    console.log('ログアウト処理を実行')
  }

  return (
    <MainLayout user={mockUser} onLogout={handleLogout}>
      {children}
    </MainLayout>
  )
}
