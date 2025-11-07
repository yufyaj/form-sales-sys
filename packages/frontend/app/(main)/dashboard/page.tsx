'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

/**
 * ダッシュボードページ
 * ユーザーのロールに応じて適切なダッシュボードにリダイレクトする
 */
export default function DashboardPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // ローディング中は何もしない
    if (isLoading || !user) return

    // ユーザーのロールに応じてリダイレクト
    switch (user.role) {
      case 'sales_company':
        router.replace('/dashboard/sales-company')
        break
      case 'customer':
        router.replace('/dashboard/customer')
        break
      case 'worker':
        router.replace('/dashboard/worker')
        break
      default:
        // ロールが不明な場合はログインページへ
        router.replace('/login')
    }
  }, [user, isLoading, router])

  // リダイレクト中はローディング表示
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
        <p className="text-gray-600">ダッシュボードを読み込んでいます...</p>
      </div>
    </div>
  )
}
