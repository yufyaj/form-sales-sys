'use client'

import Select from '@/components/ui/Select'
import type { InspectionStatus } from '@/types/list'

export interface InspectionStatusSelectorProps {
  currentStatus: InspectionStatus
  onChange: (status: InspectionStatus) => void
  disabled?: boolean
}

/**
 * 検収ステータス変更セレクターコンポーネント
 *
 * 【機能】
 * - 4つの検収ステータスから選択可能
 *   - not_started: 未検収
 *   - in_progress: 検収中
 *   - completed: 検収完了
 *   - rejected: 却下
 *
 * 【アクセシビリティ対応】
 * - aria-label属性で明確なラベルを提供
 * - キーボードナビゲーション対応（ネイティブ<select>使用）
 * - disabled状態の適切な管理
 *
 * 【設計思想】
 * - プレゼンテーショナルコンポーネント（状態管理は親に委譲）
 * - OptimisticInspectionStatusSelectorのベースとして使用
 * - 単体でも使用可能（シンプルな状態管理の場合）
 *
 * @example
 * ```tsx
 * // シンプルな使用例
 * <InspectionStatusSelector
 *   currentStatus="not_started"
 *   onChange={(status) => handleStatusChange(status)}
 *   disabled={false}
 * />
 *
 * // ローディング中の使用例
 * <InspectionStatusSelector
 *   currentStatus={status}
 *   onChange={handleChange}
 *   disabled={isLoading}
 * />
 * ```
 */
export default function InspectionStatusSelector({
  currentStatus,
  onChange,
  disabled = false,
}: InspectionStatusSelectorProps) {
  const statusOptions = [
    { value: 'not_started', label: '未検収' },
    { value: 'in_progress', label: '検収中' },
    { value: 'completed', label: '検収完了' },
    { value: 'rejected', label: '却下' },
  ]

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value as InspectionStatus)
  }

  return (
    <Select
      label="検収ステータス"
      value={currentStatus}
      onChange={handleChange}
      options={statusOptions}
      disabled={disabled}
      aria-label="検収ステータスを変更"
    />
  )
}
