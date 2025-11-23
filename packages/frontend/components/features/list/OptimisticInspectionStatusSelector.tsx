'use client'

import { useState, useOptimistic, useTransition } from 'react'
import { updateInspectionStatus } from '@/lib/actions/inspections'
import InspectionStatusSelector from './InspectionStatusSelector'
import type { InspectionStatus } from '@/types/list'

export interface OptimisticInspectionStatusSelectorProps {
  projectId: number
  listId: number
  currentStatus: InspectionStatus
  onError?: (error: Error) => void
}

/**
 * Optimistic UIを統合した検収ステータス変更セレクターコンポーネント
 * React 19のuseOptimisticフックを使用して、即座にUIを更新
 *
 * 【動作仕様】
 * - ステータス変更時、即座にUIを更新（楽観的更新）
 * - バックグラウンドでサーバー更新を実行
 * - 更新失敗時は自動的に元の状態にロールバック
 * - エラー時は親コンポーネントに通知（onErrorコールバック）
 *
 * 【注意事項】
 * - useOptimisticフックは、エラー時に自動的に元の状態に戻す
 * - しかし、ユーザーには失敗が通知されないため、onErrorで通知を実装すべき
 * - トースト通知やエラーダイアログの実装は親コンポーネントで行う
 *
 * @example
 * ```tsx
 * <OptimisticInspectionStatusSelector
 *   projectId={1}
 *   listId={1}
 *   currentStatus="not_started"
 *   onError={(error) => toast.error('ステータスの更新に失敗しました')}
 * />
 * ```
 */
export default function OptimisticInspectionStatusSelector({
  projectId,
  listId,
  currentStatus,
  onError,
}: OptimisticInspectionStatusSelectorProps) {
  const [isPending, startTransition] = useTransition()
  const [optimisticStatus, setOptimisticStatus] = useOptimistic(
    currentStatus,
    (_state, newStatus: InspectionStatus) => newStatus
  )

  const handleChange = (newStatus: InspectionStatus) => {
    // バックグラウンドでサーバー更新
    // NOTE: startTransitionを使用することで、UIのブロックを防ぐ
    // ステータス変更がバックグラウンドで実行され、ユーザーは他の操作を続けられる
    startTransition(async () => {
      // 即座にUIを更新（楽観的更新）
      // NOTE: useOptimisticフックは、transitionの中で呼び出す必要がある
      // NOTE: エラー時は自動的に元の状態に戻す
      setOptimisticStatus(newStatus)

      try {
        const result = await updateInspectionStatus(projectId, listId, newStatus)

        // サーバー更新が失敗した場合（successがfalse）
        if (!result.success) {
          throw new Error(result.error || 'ステータスの更新に失敗しました')
        }
      } catch (error) {
        // エラー時は自動的に元の状態にロールバック（useOptimisticの機能）
        console.error('ステータス更新失敗:', error)

        // 親コンポーネントにエラーを通知
        // これにより、トースト通知やエラーダイアログを表示できる
        if (onError && error instanceof Error) {
          onError(error)
        }
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
