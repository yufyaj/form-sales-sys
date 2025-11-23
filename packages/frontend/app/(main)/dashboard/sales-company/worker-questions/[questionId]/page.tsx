'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter, useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { WorkerQuestion } from '@/types/workerQuestion'
import { fetchWorkerQuestion } from '@/lib/workerQuestionApi'
import WorkerQuestionDetail from '@/components/features/worker-questions/WorkerQuestionDetail'

/**
 * 営業支援会社用ワーカー質問詳細ページ
 * 質問の詳細を表示し、回答を追加・編集
 *
 * セキュリティ:
 * - ロールベース認可チェックを実装
 * - sales_companyロール以外のユーザーは適切なダッシュボードへリダイレクト
 */
export default function WorkerQuestionDetailPage() {
  const { user, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const params = useParams()
  const questionId = Number(params.questionId)

  const [question, setQuestion] = useState<WorkerQuestion | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // ロールチェック: sales_companyロール以外はリダイレクト
    if (!authLoading && user && user.role !== 'sales_company') {
      router.replace('/dashboard')
    }
  }, [user, authLoading, router])

  useEffect(() => {
    // 質問IDの妥当性チェック
    if (isNaN(questionId) || questionId <= 0) {
      setError('無効な質問IDです')
      setIsLoading(false)
      return
    }

    // 質問詳細を取得
    const loadQuestion = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await fetchWorkerQuestion(questionId)
        setQuestion(data)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '質問の取得に失敗しました'
        )
      } finally {
        setIsLoading(false)
      }
    }

    if (user?.role === 'sales_company') {
      loadQuestion()
    }
  }, [questionId, user])

  /**
   * 質問更新時のコールバック
   */
  const handleQuestionUpdate = (updatedQuestion: WorkerQuestion) => {
    setQuestion(updatedQuestion)
  }

  // ロールチェック中はローディング表示
  if (authLoading || !user || user.role !== 'sales_company') {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  // データ取得中
  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">質問を読み込んでいます...</p>
        </div>
      </div>
    )
  }

  // エラー表示
  if (error || !question) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">エラー</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error || '質問が見つかりませんでした'}</p>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => router.back()}
                  className="text-sm font-medium text-red-800 hover:text-red-700"
                >
                  戻る
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <WorkerQuestionDetail
        question={question}
        onUpdate={handleQuestionUpdate}
      />
    </div>
  )
}
