'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import WorkerDashboard from '@/components/features/dashboard/WorkerDashboard'

/**
 * ワーカー用ダッシュボードページ
 * 割り当てリスト一覧を表示
 *
 * セキュリティ:
 * - ロールベース認可チェックを実装
 * - workerロール以外のユーザーは適切なダッシュボードへリダイレクト
 */
export default function WorkerDashboardPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // ロールチェック: workerロール以外はリダイレクト
    if (!isLoading && user && user.role !== 'worker') {
      router.replace('/dashboard')
    }
  }, [user, isLoading, router])

  // ロールチェック中はローディング表示
  if (isLoading || !user || user.role !== 'worker') {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  return <WorkerDashboard />
}
