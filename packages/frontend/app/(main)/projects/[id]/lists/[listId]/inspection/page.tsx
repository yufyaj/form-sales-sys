'use client'

import { use, useEffect, useState } from 'react'
import { useRouter, notFound } from 'next/navigation'
import Card from '@/components/ui/Card'
import InspectionStatusBadge from '@/components/features/list/InspectionStatusBadge'
import CompleteInspectionButton from '@/components/features/list/CompleteInspectionButton'
import { getInspection, completeInspection } from '@/lib/actions/inspections'
import { Inspection } from '@/types/list'
import { validatePositiveInteger, validateDate, sanitizeUserInput } from '@/lib/validation'

interface InspectionPageProps {
  params: Promise<{
    id: string
    listId: string
  }>
}

/**
 * リスト検収ページ
 */
export default function InspectionPage({ params }: InspectionPageProps) {
  const router = useRouter()
  const { id, listId } = use(params)

  // セキュリティ: 入力検証の強化 - 境界値チェック
  const projectId = validatePositiveInteger(id, 'projectId')
  const listIdNum = validatePositiveInteger(listId, 'listId')

  const [inspection, setInspection] = useState<Inspection | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCompleting, setIsCompleting] = useState(false)

  // 検証失敗時は404ページへ
  if (projectId === null || listIdNum === null) {
    notFound()
  }

  // 検収情報を取得
  useEffect(() => {
    const fetchInspection = async () => {
      try {
        // IDOR対策: projectIdとlistIdの両方を渡す
        const result = await getInspection(projectId, listIdNum)

        if (result.success && result.data) {
          setInspection(result.data)
        } else {
          setError(result.error || '検収情報の取得に失敗しました')
        }
      } catch (err) {
        console.error('Failed to fetch inspection:', err)
        setError('データの取得に失敗しました')
      } finally {
        setIsLoading(false)
      }
    }

    fetchInspection()
  }, [projectId, listIdNum])

  /**
   * 検収完了処理
   */
  const handleCompleteInspection = async () => {
    try {
      setIsCompleting(true)
      setError(null)

      // IDOR対策: projectIdとlistIdの両方を渡す
      const result = await completeInspection(projectId, listIdNum)

      if (result.success && result.data) {
        // 成功: 検収情報を更新
        setInspection(result.data)
      } else {
        setError(result.error || '検収完了処理に失敗しました')
      }
    } catch (err) {
      console.error('Failed to complete inspection:', err)
      setError('検収完了処理に失敗しました')
    } finally {
      setIsCompleting(false)
    }
  }

  /**
   * 日時フォーマット
   * セキュリティ: 無効な日付による異常動作を防ぐため、検証を実施
   */
  const formatDateTime = (dateString?: string): string => {
    const date = validateDate(dateString)

    if (!date) {
      return '-'
    }

    try {
      return date.toLocaleString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      // フォーマットエラー時のフォールバック
      return '-'
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto max-w-4xl py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">リスト検収</h1>
          <p className="text-muted-foreground">
            リストの検収状態を確認し、検収を完了します
          </p>
        </div>
        <Card>
          <div className="flex h-64 items-center justify-center">
            <div className="text-muted-foreground">読み込み中...</div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-4xl py-8 space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">リスト検収</h1>
          <p className="text-muted-foreground">
            リストの検収状態を確認し、検収を完了します
          </p>
        </div>
      </div>

      {/* エラーメッセージ */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* 検収情報 */}
      {inspection && (
        <Card>
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">検収ステータス</h2>
              <div className="flex items-center gap-3">
                <InspectionStatusBadge
                  status={inspection.status}
                  size="lg"
                />
              </div>
            </div>

            {/* 検収詳細 */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium mb-4">検収詳細</h3>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    検収者
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {/* セキュリティ: XSS対策 - ユーザー入力をサニタイズ */}
                    {sanitizeUserInput(inspection.inspectedBy, 100)}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    検収日時
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {formatDateTime(inspection.inspectedAt)}
                  </dd>
                </div>

                {inspection.comment && (
                  <div className="sm:col-span-2">
                    <dt className="text-sm font-medium text-gray-500">
                      コメント
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {/* セキュリティ: XSS対策 - コメントをサニタイズ（最大1000文字） */}
                      {sanitizeUserInput(inspection.comment, 1000)}
                    </dd>
                  </div>
                )}
              </dl>
            </div>

            {/* 検収完了ボタン */}
            {inspection.status !== 'completed' &&
              inspection.status !== 'rejected' && (
                <div className="border-t pt-6">
                  <div className="flex justify-end">
                    <CompleteInspectionButton
                      onComplete={handleCompleteInspection}
                      isLoading={isCompleting}
                      showConfirm
                      confirmMessage="検収を完了してもよろしいですか？この操作は取り消せません。"
                    />
                  </div>
                </div>
              )}
          </div>
        </Card>
      )}
    </div>
  )
}
