'use client'

import { cn } from '@/lib/utils'

interface DateInputSingleProps {
  mode?: 'single'
  value: string
  onChange: (value: string) => void
  startDate?: never
  endDate?: never
  onStartDateChange?: never
  onEndDateChange?: never
  label?: string
  description?: string
  error?: string
  disabled?: boolean
}

interface DateInputRangeProps {
  mode: 'range'
  startDate: string
  endDate: string
  onStartDateChange: (value: string) => void
  onEndDateChange: (value: string) => void
  value?: never
  onChange?: never
  label?: string
  description?: string
  error?: string
  disabled?: boolean
}

type DateInputProps = DateInputSingleProps | DateInputRangeProps

/**
 * 日付入力コンポーネント
 * 単一日付または期間選択モードをサポート
 */
export default function DateInput(props: DateInputProps) {
  const { label, description, error, disabled = false } = props

  const isRangeMode = props.mode === 'range'

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

      {isRangeMode ? (
        /* 期間選択モード */
        <div className="grid grid-cols-2 gap-4">
          {/* 開始日 */}
          <div>
            <label
              htmlFor="date-start"
              className="block text-xs font-medium text-gray-600 mb-1"
            >
              開始日
            </label>
            <input
              type="date"
              id="date-start"
              value={props.startDate}
              onChange={(e) => props.onStartDateChange(e.target.value)}
              disabled={disabled}
              aria-invalid={!!error}
              aria-describedby={error ? 'date-error' : undefined}
              className={cn(
                'w-full px-3 py-2 border rounded-md shadow-sm',
                'text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                error
                  ? 'border-red-300 text-red-900 focus:ring-red-500 focus:border-red-500'
                  : 'border-gray-300 text-gray-900',
                disabled && 'bg-gray-100 cursor-not-allowed opacity-50'
              )}
            />
          </div>

          {/* 終了日 */}
          <div>
            <label
              htmlFor="date-end"
              className="block text-xs font-medium text-gray-600 mb-1"
            >
              終了日
            </label>
            <input
              type="date"
              id="date-end"
              value={props.endDate}
              onChange={(e) => props.onEndDateChange(e.target.value)}
              disabled={disabled}
              aria-invalid={!!error}
              aria-describedby={error ? 'date-error' : undefined}
              className={cn(
                'w-full px-3 py-2 border rounded-md shadow-sm',
                'text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                error
                  ? 'border-red-300 text-red-900 focus:ring-red-500 focus:border-red-500'
                  : 'border-gray-300 text-gray-900',
                disabled && 'bg-gray-100 cursor-not-allowed opacity-50'
              )}
            />
          </div>
        </div>
      ) : (
        /* 単一日付モード */
        <div>
          <label htmlFor="date" className="sr-only">
            日付
          </label>
          <input
            type="date"
            id="date"
            aria-label="日付"
            value={props.value}
            onChange={(e) => props.onChange(e.target.value)}
            disabled={disabled}
            aria-invalid={!!error}
            aria-describedby={error ? 'date-error' : undefined}
            className={cn(
              'w-full px-3 py-2 border rounded-md shadow-sm',
              'text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              error
                ? 'border-red-300 text-red-900 focus:ring-red-500 focus:border-red-500'
                : 'border-gray-300 text-gray-900',
              disabled && 'bg-gray-100 cursor-not-allowed opacity-50'
            )}
          />
        </div>
      )}

      {/* エラーメッセージ */}
      {error && (
        <p role="alert" id="date-error" className="text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  )
}
