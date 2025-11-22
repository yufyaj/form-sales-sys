'use client'

import { cn } from '@/lib/utils'

interface TimeRangeInputProps {
  timeStart: string
  timeEnd: string
  onTimeStartChange: (value: string) => void
  onTimeEndChange: (value: string) => void
  label?: string
  description?: string
  error?: string
  disabled?: boolean
  placeholderStart?: string
  placeholderEnd?: string
  showSeconds?: boolean
}

/**
 * 時間帯入力コンポーネント
 * 開始時刻と終了時刻を入力するフィールドを提供
 */
export default function TimeRangeInput({
  timeStart,
  timeEnd,
  onTimeStartChange,
  onTimeEndChange,
  label,
  description,
  error,
  disabled = false,
  placeholderStart = 'HH:MM',
  placeholderEnd = 'HH:MM',
  showSeconds = false,
}: TimeRangeInputProps) {
  const inputType = showSeconds ? 'time' : 'time'
  const step = showSeconds ? 1 : 60 // 秒単位か分単位か

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}

      {description && (
        <p className="text-sm text-gray-500">{description}</p>
      )}

      <div className="grid grid-cols-2 gap-4">
        {/* 開始時刻 */}
        <div>
          <label
            htmlFor="time-start"
            className="block text-xs font-medium text-gray-600 mb-1"
          >
            開始時刻
          </label>
          <input
            type={inputType}
            id="time-start"
            value={timeStart}
            onChange={(e) => onTimeStartChange(e.target.value)}
            disabled={disabled}
            placeholder={placeholderStart}
            step={step}
            aria-invalid={!!error}
            aria-describedby={error ? 'time-range-error' : undefined}
            className={cn(
              'w-full px-3 py-2 border rounded-md shadow-sm',
              'text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              error
                ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 text-gray-900 placeholder-gray-400',
              disabled && 'bg-gray-100 cursor-not-allowed opacity-50'
            )}
          />
        </div>

        {/* 終了時刻 */}
        <div>
          <label
            htmlFor="time-end"
            className="block text-xs font-medium text-gray-600 mb-1"
          >
            終了時刻
          </label>
          <input
            type={inputType}
            id="time-end"
            value={timeEnd}
            onChange={(e) => onTimeEndChange(e.target.value)}
            disabled={disabled}
            placeholder={placeholderEnd}
            step={step}
            aria-invalid={!!error}
            aria-describedby={error ? 'time-range-error' : undefined}
            className={cn(
              'w-full px-3 py-2 border rounded-md shadow-sm',
              'text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              error
                ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 text-gray-900 placeholder-gray-400',
              disabled && 'bg-gray-100 cursor-not-allowed opacity-50'
            )}
          />
        </div>
      </div>

      {/* エラーメッセージ */}
      {error && (
        <p role="alert" id="time-range-error" className="text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  )
}
