'use client'

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/Dialog'
import Badge from '@/components/ui/Badge'
import type { WorkerQuestion, QuestionStatus, QuestionPriority } from '@/types/question'

interface QuestionDetailDialogProps {
  question: WorkerQuestion | null
  isOpen: boolean
  onClose: () => void
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
 * ワーカー質問詳細ダイアログコンポーネント
 *
 * 質問の詳細情報と回答を表示
 */
export default function QuestionDetailDialog({
  question,
  isOpen,
  onClose,
}: QuestionDetailDialogProps) {
  if (!question) {
    return null
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{question.title}</DialogTitle>
          <DialogDescription>
            投稿日時:{' '}
            {new Date(question.createdAt).toLocaleString('ja-JP', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* ステータスと優先度 */}
          <div className="flex items-center gap-4">
            <div>
              <span className="text-sm text-gray-600">ステータス: </span>
              <Badge variant={getStatusVariant(question.status)}>
                {getStatusLabel(question.status)}
              </Badge>
            </div>
            <div>
              <span className="text-sm text-gray-600">優先度: </span>
              <Badge variant={getPriorityVariant(question.priority)}>
                {getPriorityLabel(question.priority)}
              </Badge>
            </div>
          </div>

          {/* 質問内容 */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">質問内容</h3>
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="whitespace-pre-wrap text-sm text-gray-900">
                {question.content}
              </p>
            </div>
          </div>

          {/* 回答 */}
          {question.answer ? (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                回答
                {question.answeredAt && (
                  <span className="ml-2 text-xs font-normal text-gray-500">
                    {new Date(question.answeredAt).toLocaleString('ja-JP', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                )}
              </h3>
              <div className="rounded-lg bg-blue-50 p-4">
                <p className="whitespace-pre-wrap text-sm text-gray-900">
                  {question.answer}
                </p>
              </div>
            </div>
          ) : (
            <div className="rounded-lg bg-yellow-50 p-4">
              <p className="text-sm text-yellow-800">まだ回答がありません</p>
            </div>
          )}

          {/* タグ（オプション） */}
          {question.tags && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">タグ</h3>
              <div className="flex flex-wrap gap-2">
                {(() => {
                  try {
                    const parsedTags = JSON.parse(question.tags)
                    if (!Array.isArray(parsedTags)) {
                      console.warn('Tags is not an array:', question.tags)
                      return null
                    }
                    return parsedTags
                      .filter((tag): tag is string => typeof tag === 'string')
                      .map((tag, index) => (
                        <Badge key={index} variant="default" size="sm">
                          {tag}
                        </Badge>
                      ))
                  } catch (error) {
                    console.error('Failed to parse tags:', error)
                    return null
                  }
                })()}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
