'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import CustomerDashboard from '@/components/features/dashboard/CustomerDashboard'

/**
 * 顧客用ダッシュボードページ
 * 依頼プロジェクト一覧を表示
 *
 * セキュリティ:
 * - ロールベース認可チェックを実装
 * - customerロール以外のユーザーは適切なダッシュボードへリダイレクト
 */
export default function CustomerDashboardPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // ロールチェック: customerロール以外はリダイレクト
    if (!isLoading && user && user.role !== 'customer') {
      router.replace('/dashboard')
    }
  }, [user, isLoading, router])

  // ロールチェック中はローディング表示
  if (isLoading || !user || user.role !== 'customer') {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  return <CustomerDashboard />
}
