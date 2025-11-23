'use client'

import { useOptimistic, useTransition } from 'react'
import { updateInspectionStatus } from '@/lib/actions/inspections'
import InspectionStatusSelector from './InspectionStatusSelector'
import type { InspectionStatus } from '@/types/list'

export interface OptimisticInspectionStatusSelectorProps {
  projectId: number
  listId: number
  currentStatus: InspectionStatus
}

/**
 * Optimistic UIを統合した検収ステータス変更セレクターコンポーネント
 * React 19のuseOptimisticフックを使用して、即座にUIを更新
 *
 * @example
 * ```tsx
 * <OptimisticInspectionStatusSelector
 *   projectId={1}
 *   listId={1}
 *   currentStatus="not_started"
 * />
 * ```
 */
export default function OptimisticInspectionStatusSelector({
  projectId,
  listId,
  currentStatus,
}: OptimisticInspectionStatusSelectorProps) {
  const [isPending, startTransition] = useTransition()
  const [optimisticStatus, setOptimisticStatus] = useOptimistic(
    currentStatus,
    (_state, newStatus: InspectionStatus) => newStatus
  )

  const handleChange = (newStatus: InspectionStatus) => {
    // 即座にUIを更新（楽観的更新）
    setOptimisticStatus(newStatus)

    // バックグラウンドでサーバー更新
    startTransition(async () => {
      try {
        await updateInspectionStatus(projectId, listId, newStatus)
      } catch (error) {
        // エラー時は自動的に元の状態にロールバック
        console.error('ステータス更新失敗:', error)
      }
    })
  }

  return (
    <InspectionStatusSelector
      currentStatus={optimisticStatus}
      onChange={handleChange}
      disabled={isPending}
    />
  )
}
