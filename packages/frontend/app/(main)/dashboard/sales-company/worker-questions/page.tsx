'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import WorkerQuestionList from '@/components/features/worker-questions/WorkerQuestionList'

/**
 * 営業支援会社用ワーカー質問管理ページ
 * ワーカーからの質問一覧を表示し、回答を管理
 *
 * セキュリティ:
 * - ロールベース認可チェックを実装
 * - sales_companyロール以外のユーザーは適切なダッシュボードへリダイレクト
 */
export default function WorkerQuestionsPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // ロールチェック: sales_companyロール以外はリダイレクト
    if (!isLoading && user && user.role !== 'sales_company') {
      router.replace('/dashboard')
    }
  }, [user, isLoading, router])

  // ロールチェック中はローディング表示
  if (isLoading || !user || user.role !== 'sales_company') {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">ワーカー質問管理</h1>
        <p className="mt-2 text-gray-600">
          ワーカーからの質問を確認し、回答を提供します
        </p>
      </div>
      <WorkerQuestionList />
    </div>
  )
}
