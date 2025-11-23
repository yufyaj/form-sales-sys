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
 * @example
 * ```tsx
 * <InspectionStatusSelector
 *   currentStatus="not_started"
 *   onChange={(status) => console.log(status)}
 *   disabled={false}
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
