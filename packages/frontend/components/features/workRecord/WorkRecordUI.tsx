/**
 * 作業記録UI統合コンポーネント
 * 作業時間表示、禁止時間帯チェック、送信ボタンを統合
 *
 * Phase5要件:
 * - 送信済みボタン
 * - 送信不可ボタン
 * - 作業日時表示（自動記録）
 * - 送信制御UI（禁止時間帯の警告・ボタン無効化）
 */

'use client'

import { useState, useEffect } from 'react'
import WorkTimeDisplay from './WorkTimeDisplay'
import WorkRecordButtons from './WorkRecordButtons'
import { useProhibitedTimeCheck } from '@/hooks/useProhibitedTimeCheck'
import { getNoSendSettings } from '@/lib/actions/noSendSettings'
import type { NoSendSetting } from '@/types/noSendSetting'

export interface WorkRecordUIProps {
  /** 割り当てID */
  assignmentId: number
  /** リストID（禁止設定取得用） */
  listId: number
  /** 作業記録完了時のコールバック */
  onRecordCreated?: () => void
}

/**
 * 作業記録UI統合コンポーネント
 */
export default function WorkRecordUI({
  assignmentId,
  listId,
  onRecordCreated,
}: WorkRecordUIProps) {
  // 作業開始時刻（コンポーネントマウント時に記録）
  const [startedAt] = useState(() => new Date().toISOString())

  // 送信禁止設定
  const [noSendSettings, setNoSendSettings] = useState<NoSendSetting[]>([])
  const [isLoadingSettings, setIsLoadingSettings] = useState(true)

  // 送信禁止設定を取得
  useEffect(() => {
    async function fetchNoSendSettings() {
      setIsLoadingSettings(true)
      try {
        const result = await getNoSendSettings(listId)
        if (result.success && result.data) {
          setNoSendSettings(result.data)
        }
      } catch (error) {
        console.error('送信禁止設定取得エラー:', error)
      } finally {
        setIsLoadingSettings(false)
      }
    }

    fetchNoSendSettings()
  }, [listId])

  // 禁止時間帯チェック（リアルタイム）
  const prohibitedCheck = useProhibitedTimeCheck(noSendSettings)

  if (isLoadingSettings) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">設定を読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div>
        <h2 className="text-xl font-bold text-gray-900">作業記録</h2>
        <p className="mt-1 text-sm text-gray-600">
          作業を完了したら、送信済みまたは送信不可を記録してください。
        </p>
      </div>

      {/* 作業時間表示 */}
      <WorkTimeDisplay startedAt={startedAt} />

      {/* 作業記録ボタン */}
      <WorkRecordButtons
        assignmentId={assignmentId}
        prohibitedCheck={prohibitedCheck}
        startedAt={startedAt}
        onRecordCreated={onRecordCreated}
      />

      {/* 注意事項 */}
      <div className="rounded-md bg-blue-50 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-blue-400"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-blue-800">記録についての注意</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-inside list-disc space-y-1">
                <li>作業開始時刻は自動的に記録されます</li>
                <li>送信済みボタンは禁止時間帯には無効化されます</li>
                <li>送信不可の場合は理由を選択してください</li>
                <li>記録後は取り消しができませんのでご注意ください</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
