'use client'

import { useEffect, useState } from 'react'
import Table, { type Column } from '@/components/ui/Table'
import Badge from '@/components/ui/Badge'
import type { WorkerQuestion, QuestionStatus, QuestionPriority } from '@/types/question'
import { getQuestionsByClientOrganizationAction } from '@/lib/actions/questions'

interface QuestionHistoryTableProps {
  clientOrganizationId: number
  onQuestionClick?: (question: WorkerQuestion) => void
  refreshTrigger?: number // 外部からリフレッシュをトリガーするためのプロップ
}

/**
 * 質問ステータスのバリアント取得
 */
function getStatusVariant(
  status: QuestionStatus
): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  const variantMap: Record<QuestionStatus, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
    pending: 'warning',
    in_review: 'info',
    answered: 'success',
    closed: 'default',
  }
  return variantMap[status] || 'default'
}

/**
 * 質問ステータスの日本語表示
 */
function getStatusLabel(status: QuestionStatus): string {
  const labelMap: Record<QuestionStatus, string> = {
    pending: '未対応',
    in_review: '確認中',
    answered: '回答済み',
    closed: '完了',
  }
  return labelMap[status] || status
}

/**
 * 優先度のバリアント取得
 */
function getPriorityVariant(
  priority: QuestionPriority
): 'default' | 'success' | 'warning' | 'danger' {
  const variantMap: Record<QuestionPriority, 'default' | 'success' | 'warning' | 'danger'> = {
    low: 'default',
    medium: 'info',
    high: 'danger',
  }
  return variantMap[priority] || 'default'
}

/**
 * 優先度の日本語表示
 */
function getPriorityLabel(priority: QuestionPriority): string {
  const labelMap: Record<QuestionPriority, string> = {
    low: '低',
    medium: '中',
    high: '高',
  }
  return labelMap[priority] || priority
}

/**
 * ワーカー質問履歴テーブルコンポーネント
 *
 * 顧客組織に関連する質問一覧を表示
 */
export default function QuestionHistoryTable({
  clientOrganizationId,
  onQuestionClick,
  refreshTrigger = 0,
}: QuestionHistoryTableProps) {
  const [questions, setQuestions] = useState<WorkerQuestion[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')

  // 質問一覧を取得
  useEffect(() => {
    async function fetchQuestions() {
      setIsLoading(true)
      setError('')

      try {
        const result = await getQuestionsByClientOrganizationAction(
          clientOrganizationId,
          {
            limit: 100,
          }
        )

        if (!result.success) {
          setError(result.error)
          return
        }

        setQuestions(result.data.questions)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : '質問一覧の取得に失敗しました'
        )
      } finally {
        setIsLoading(false)
      }
    }

    fetchQuestions()
  }, [clientOrganizationId, refreshTrigger])

  const columns: Column<WorkerQuestion>[] = [
    {
      key: 'createdAt',
      header: '投稿日時',
      render: (question) =>
        new Date(question.createdAt).toLocaleString('ja-JP', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        }),
    },
    {
      key: 'title',
      header: '質問タイトル',
      render: (question) => (
        <div className="max-w-md">
          <div className="truncate font-medium">{question.title}</div>
        </div>
      ),
    },
    {
      key: 'priority',
      header: '優先度',
      align: 'center',
      render: (question) => (
        <Badge variant={getPriorityVariant(question.priority)} size="sm">
          {getPriorityLabel(question.priority)}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'ステータス',
      align: 'center',
      render: (question) => (
        <Badge variant={getStatusVariant(question.status)} size="sm">
          {getStatusLabel(question.status)}
        </Badge>
      ),
    },
    {
      key: 'answeredAt',
      header: '回答日時',
      render: (question) =>
        question.answeredAt
          ? new Date(question.answeredAt).toLocaleString('ja-JP', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
            })
          : '-',
    },
  ]

  if (isLoading) {
    return (
      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow">
        <div className="p-12 text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-500">読み込み中...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="overflow-hidden rounded-lg border border-red-200 bg-white shadow">
        <div className="p-12 text-center">
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <Table
      columns={columns}
      data={questions}
      keyExtractor={(question) => question.id.toString()}
      onRowClick={onQuestionClick}
      emptyMessage="質問履歴がありません"
    />
  )
}
