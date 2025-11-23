/**
 * 作業時間表示コンポーネント
 * 作業開始時刻と経過時間をリアルタイム表示
 */

'use client'

import { useState, useEffect } from 'react'

export interface WorkTimeDisplayProps {
  /** 作業開始時刻（ISO 8601形式） */
  startedAt: string
  /** 表示を更新する間隔（ミリ秒）デフォルト: 1000ms */
  updateInterval?: number
}

/**
 * 経過時間を「〇時間〇分〇秒」形式で表示
 */
function formatElapsedTime(milliseconds: number): string {
  const totalSeconds = Math.floor(milliseconds / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  const parts: string[] = []
  if (hours > 0) parts.push(`${hours}時間`)
  if (minutes > 0) parts.push(`${minutes}分`)
  parts.push(`${seconds}秒`)

  return parts.join('')
}

/**
 * 作業時間表示コンポーネント
 */
export default function WorkTimeDisplay({
  startedAt,
  updateInterval = 1000,
}: WorkTimeDisplayProps) {
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    // 経過時間を計算
    const calculateElapsed = () => {
      const start = new Date(startedAt)
      const now = new Date()
      return now.getTime() - start.getTime()
    }

    // 初回計算
    setElapsedTime(calculateElapsed())

    // 定期更新
    const intervalId = setInterval(() => {
      setElapsedTime(calculateElapsed())
    }, updateInterval)

    // クリーンアップ
    return () => {
      clearInterval(intervalId)
    }
  }, [startedAt, updateInterval])

  // 作業開始時刻のフォーマット
  const startedAtDate = new Date(startedAt)
  const formattedStartTime = startedAtDate.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="space-y-3">
        {/* 作業開始時刻 */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-500">作業開始時刻</span>
          <time
            dateTime={startedAt}
            className="text-sm font-semibold text-gray-900"
          >
            {formattedStartTime}
          </time>
        </div>

        {/* 経過時間 */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-500">経過時間</span>
          <span
            className="text-sm font-semibold text-blue-600"
            role="timer"
            aria-live="off"
            aria-atomic="true"
          >
            {formatElapsedTime(elapsedTime)}
          </span>
        </div>
      </div>
    </div>
  )
}
