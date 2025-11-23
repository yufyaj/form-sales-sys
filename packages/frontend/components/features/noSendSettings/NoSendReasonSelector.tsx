'use client'

import { NoSendReason } from '@/types/noSendReason'
import { cn } from '@/lib/utils'

interface NoSendReasonSelectorProps {
  reasons: NoSendReason[]
  value: string[]
  onChange: (value: string[]) => void
  label?: string
  error?: string
  disabled?: boolean
  showSelectAll?: boolean
}

/**
 * 送信不可理由選択コンポーネント
 * 複数の理由をチェックボックスで選択できるUI
 * デフォルト理由とカスタム理由を区別して表示
 */
export default function NoSendReasonSelector({
  reasons,
  value,
  onChange,
  label,
  error,
  disabled = false,
  showSelectAll = false,
}: NoSendReasonSelectorProps) {
  /**
   * 理由の選択/選択解除をトグル
   */
  const handleToggleReason = (reasonId: string) => {
    if (disabled) return

    if (value.includes(reasonId)) {
      // 選択解除
      onChange(value.filter((id) => id !== reasonId))
    } else {
      // 選択
      onChange([...value, reasonId])
    }
  }

  /**
   * 全理由を選択
   */
  const handleSelectAll = () => {
    if (disabled) return

    onChange(reasons.map((reason) => reason.id))
  }

  /**
   * 全選択を解除
   */
  const handleClearAll = () => {
    if (disabled) return

    onChange([])
  }

  // デフォルト理由とカスタム理由に分類
  const defaultReasons = reasons.filter((r) => r.isDefault)
  const customReasons = reasons.filter((r) => !r.isDefault)

  /**
   * チェックボックス項目をレンダリング
   */
  const renderCheckboxItem = (reason: NoSendReason) => {
    const isChecked = value.includes(reason.id)

    return (
      <label
        key={reason.id}
        className={cn(
          'flex items-center gap-3 p-3 rounded-lg border cursor-pointer',
          'transition-colors duration-200',
          'hover:bg-gray-50',
          isChecked && 'bg-blue-50 border-blue-300',
          !isChecked && 'border-gray-200',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <input
          type="checkbox"
          checked={isChecked}
          onChange={() => handleToggleReason(reason.id)}
          disabled={disabled}
          className={cn(
            'w-4 h-4 rounded border-gray-300',
            'text-blue-600 focus:ring-blue-500 focus:ring-offset-2',
            'transition-colors duration-200',
            disabled && 'cursor-not-allowed'
          )}
        />
        <span
          className={cn(
            'text-sm font-medium',
            isChecked ? 'text-blue-900' : 'text-gray-700'
          )}
        >
          {reason.label}
        </span>
      </label>
    )
  }

  return (
    <div className="space-y-4">
      {/* ラベル */}
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}

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

      {/* デフォルト理由セクション */}
      {defaultReasons.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            デフォルト理由
          </h3>
          <div className="space-y-2">
            {defaultReasons.map((reason) => renderCheckboxItem(reason))}
          </div>
        </div>
      )}

      {/* カスタム理由セクション */}
      {customReasons.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            カスタム理由
          </h3>
          <div className="space-y-2">
            {customReasons.map((reason) => renderCheckboxItem(reason))}
          </div>
        </div>
      )}

      {/* エラーメッセージ */}
      {error && (
        <p role="alert" className="text-sm text-red-600 mt-2">
          {error}
        </p>
      )}
    </div>
  )
}
