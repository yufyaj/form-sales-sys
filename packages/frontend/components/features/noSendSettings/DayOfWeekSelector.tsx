'use client'

import { DayOfWeek, DAY_OF_WEEK_LABELS } from '@/types/noSendSetting'
import { cn } from '@/lib/utils'

interface DayOfWeekSelectorProps {
  value: DayOfWeek[]
  onChange: (value: DayOfWeek[]) => void
  label?: string
  error?: string
  disabled?: boolean
  showSelectAll?: boolean
}

/**
 * 曜日選択コンポーネント
 * 複数の曜日を選択できるトグルボタン群を提供
 */
export default function DayOfWeekSelector({
  value,
  onChange,
  label,
  error,
  disabled = false,
  showSelectAll = false,
}: DayOfWeekSelectorProps) {
  /**
   * 曜日の選択/選択解除をトグル
   */
  const handleToggleDay = (day: DayOfWeek) => {
    if (disabled) return

    if (value.includes(day)) {
      // 選択解除
      onChange(value.filter((d) => d !== day))
    } else {
      // 選択
      onChange([...value, day].sort((a, b) => a - b))
    }
  }

  /**
   * 全曜日を選択
   */
  const handleSelectAll = () => {
    if (disabled) return

    onChange([
      DayOfWeek.MONDAY,
      DayOfWeek.TUESDAY,
      DayOfWeek.WEDNESDAY,
      DayOfWeek.THURSDAY,
      DayOfWeek.FRIDAY,
      DayOfWeek.SATURDAY,
      DayOfWeek.SUNDAY,
    ])
  }

  /**
   * 全選択を解除
   */
  const handleClearAll = () => {
    if (disabled) return

    onChange([])
  }

  // 曜日リスト（月〜日の順）
  const weekDays: DayOfWeek[] = [
    DayOfWeek.MONDAY,
    DayOfWeek.TUESDAY,
    DayOfWeek.WEDNESDAY,
    DayOfWeek.THURSDAY,
    DayOfWeek.FRIDAY,
    DayOfWeek.SATURDAY,
    DayOfWeek.SUNDAY,
  ]

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}

      <div className="space-y-3">
        {/* 曜日ボタン群 */}
        <div className="flex flex-wrap gap-2">
          {weekDays.map((day) => {
            const isSelected = value.includes(day)
            return (
              <button
                key={day}
                type="button"
                role="button"
                aria-pressed={isSelected}
                disabled={disabled}
                onClick={() => handleToggleDay(day)}
                className={cn(
                  'min-w-[3rem] px-4 py-2 rounded-md text-sm font-medium',
                  'transition-colors duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
                  isSelected
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
                  disabled && 'opacity-50 cursor-not-allowed',
                  // 土日は特別な色
                  !isSelected &&
                    day === DayOfWeek.SATURDAY &&
                    'bg-blue-50 text-blue-700',
                  !isSelected &&
                    day === DayOfWeek.SUNDAY &&
                    'bg-red-50 text-red-700'
                )}
              >
                {DAY_OF_WEEK_LABELS[day]}
              </button>
            )
          })}
        </div>

        {/* 全選択/全解除ボタン */}
        {showSelectAll && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleSelectAll}
              disabled={disabled}
              className={cn(
                'px-3 py-1 text-xs font-medium rounded',
                'bg-gray-50 text-gray-600 hover:bg-gray-100',
                'transition-colors duration-200',
                'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400',
                disabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              全て選択
            </button>
            <button
              type="button"
              onClick={handleClearAll}
              disabled={disabled}
              className={cn(
                'px-3 py-1 text-xs font-medium rounded',
                'bg-gray-50 text-gray-600 hover:bg-gray-100',
                'transition-colors duration-200',
                'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400',
                disabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              全て解除
            </button>
          </div>
        )}
      </div>

      {/* エラーメッセージ */}
      {error && (
        <p role="alert" className="text-sm text-red-600 mt-1">
          {error}
        </p>
      )}
    </div>
  )
}
