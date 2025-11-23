/**
 * 作業記録ボタンコンポーネント
 * 送信済み・送信不可ボタンを提供
 *
 * セキュリティ:
 * - クライアント側での禁止時間帯チェックはUI表示用
 * - 実際の作成可否はサーバー側で再検証される
 * - ARIA属性による適切なアクセシビリティサポート
 */

'use client'

import { useState, useEffect } from 'react'
import Button from '@/components/ui/Button'
import { createSentWorkRecord, createCannotSendWorkRecord, getCannotSendReasons } from '@/lib/actions/workRecord'
import type { CannotSendReason } from '@/types/workRecord'
import type { ProhibitedTimeCheckResult } from '@/types/workRecord'

export interface WorkRecordButtonsProps {
  /** 割り当てID */
  assignmentId: number
  /** 禁止時間帯チェック結果 */
  prohibitedCheck: ProhibitedTimeCheckResult
  /** 作業開始時刻（ISO 8601形式） */
  startedAt: string
  /** 作業記録完了時のコールバック */
  onRecordCreated?: () => void
}

/**
 * 作業記録ボタンコンポーネント
 */
export default function WorkRecordButtons({
  assignmentId,
  prohibitedCheck,
  startedAt,
  onRecordCreated,
}: WorkRecordButtonsProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showCannotSendDialog, setShowCannotSendDialog] = useState(false)
  const [cannotSendReasons, setCannotSendReasons] = useState<CannotSendReason[]>([])
  const [selectedReasonId, setSelectedReasonId] = useState<number | null>(null)
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)

  // 送信不可理由一覧を取得
  useEffect(() => {
    let isMounted = true

    async function fetchReasons() {
      try {
        const result = await getCannotSendReasons()
        // コンポーネントがまだマウントされている場合のみ状態を更新
        if (isMounted && result.success && result.data) {
          setCannotSendReasons(result.data.filter((r) => r.is_active))
        }
      } catch (error) {
        console.error('送信不可理由取得エラー:', error)
      }
    }

    fetchReasons()

    // クリーンアップ関数でマウント状態を更新
    return () => {
      isMounted = false
    }
  }, [])

  // 送信済みボタンクリック
  const handleSentClick = async () => {
    if (prohibitedCheck.isProhibited) {
      return // 禁止時間帯はボタン無効化されているが念のため
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const completedAt = new Date().toISOString()
      const result = await createSentWorkRecord({
        assignment_id: assignmentId,
        started_at: startedAt,
        completed_at: completedAt,
        notes: notes || undefined,
      })

      if (result.success) {
        // 成功時のコールバック
        onRecordCreated?.()
        // フォームリセット
        setNotes('')
      } else {
        setError(result.error || '送信済み記録の作成に失敗しました')
      }
    } catch (err) {
      setError('予期しないエラーが発生しました')
      console.error('送信済み記録作成エラー:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  // 送信不可ボタンクリック
  const handleCannotSendClick = () => {
    setShowCannotSendDialog(true)
  }

  // 送信不可記録確定
  const handleCannotSendSubmit = async () => {
    if (!selectedReasonId) {
      setError('送信不可理由を選択してください')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const completedAt = new Date().toISOString()
      const result = await createCannotSendWorkRecord({
        assignment_id: assignmentId,
        started_at: startedAt,
        completed_at: completedAt,
        cannot_send_reason_id: selectedReasonId,
        notes: notes || undefined,
      })

      if (result.success) {
        // 成功時のコールバック
        onRecordCreated?.()
        // フォームリセット
        setShowCannotSendDialog(false)
        setSelectedReasonId(null)
        setNotes('')
      } else {
        setError(result.error || '送信不可記録の作成に失敗しました')
      }
    } catch (err) {
      setError('予期しないエラーが発生しました')
      console.error('送信不可記録作成エラー:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* エラーメッセージ */}
      {error && (
        <div
          className="rounded-md bg-red-50 p-4 text-sm text-red-800"
          role="alert"
          aria-live="polite"
        >
          {error}
        </div>
      )}

      {/* 禁止時間帯警告 */}
      {prohibitedCheck.isProhibited && (
        <div
          id="prohibited-warning"
          className="rounded-md bg-yellow-50 p-4"
          role="alert"
          aria-live="polite"
        >
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">送信禁止時間帯</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>現在は送信禁止時間帯です。以下の理由により送信できません：</p>
                <ul className="mt-1 list-inside list-disc space-y-1">
                  {prohibitedCheck.reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
                {prohibitedCheck.nextAllowedTime && (
                  <p className="mt-2">
                    次回送信可能時刻:{' '}
                    {prohibitedCheck.nextAllowedTime.toLocaleString('ja-JP')}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* メモ入力 */}
      <div>
        <label htmlFor="work-notes" className="block text-sm font-medium text-gray-700">
          メモ（任意）
        </label>
        <textarea
          id="work-notes"
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          placeholder="作業に関するメモを入力..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          disabled={isSubmitting}
        />
      </div>

      {/* ボタングループ */}
      <div className="flex gap-4">
        <Button
          variant="default"
          size="lg"
          onClick={handleSentClick}
          disabled={prohibitedCheck.isProhibited || isSubmitting}
          isLoading={isSubmitting}
          aria-label="送信済みとして記録"
          aria-disabled={prohibitedCheck.isProhibited ? 'true' : undefined}
          aria-describedby={prohibitedCheck.isProhibited ? 'prohibited-warning' : undefined}
          className="flex-1"
        >
          送信済み
        </Button>

        <Button
          variant="destructive"
          size="lg"
          onClick={handleCannotSendClick}
          disabled={isSubmitting}
          isLoading={isSubmitting}
          aria-label="送信不可として記録"
          className="flex-1"
        >
          送信不可
        </Button>
      </div>

      {/* 送信不可ダイアログ（シンプルなモーダル） */}
      {showCannotSendDialog && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
          role="dialog"
          aria-modal="true"
          aria-labelledby="dialog-title"
        >
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h3 id="dialog-title" className="mb-4 text-lg font-medium text-gray-900">
              送信不可理由の選択
            </h3>

            <div className="space-y-4">
              <div>
                <label htmlFor="cannot-send-reason" className="block text-sm font-medium text-gray-700">
                  理由を選択してください
                </label>
                <select
                  id="cannot-send-reason"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  value={selectedReasonId || ''}
                  onChange={(e) => setSelectedReasonId(Number(e.target.value))}
                  disabled={isSubmitting}
                >
                  <option value="">選択してください</option>
                  {cannotSendReasons.map((reason) => (
                    <option key={reason.id} value={reason.id}>
                      {reason.reason_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowCannotSendDialog(false)
                    setSelectedReasonId(null)
                    setError(null)
                  }}
                  disabled={isSubmitting}
                >
                  キャンセル
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleCannotSendSubmit}
                  disabled={!selectedReasonId || isSubmitting}
                  isLoading={isSubmitting}
                >
                  記録する
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
