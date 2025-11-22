'use client'

import Button from '@/components/ui/Button'

interface CompleteInspectionButtonProps {
  onComplete: () => void | Promise<void>
  disabled?: boolean
  isLoading?: boolean
  showConfirm?: boolean
  confirmMessage?: string
}

/**
 * 検収完了ボタンコンポーネント
 * 検収を完了するためのボタン
 */
export default function CompleteInspectionButton({
  onComplete,
  disabled = false,
  isLoading = false,
  showConfirm = false,
  confirmMessage = '検収を完了してもよろしいですか？',
}: CompleteInspectionButtonProps) {
  /**
   * ボタンクリックハンドラ
   * 確認ダイアログが有効な場合は確認を表示
   */
  const handleClick = async () => {
    if (showConfirm) {
      if (!window.confirm(confirmMessage)) {
        return
      }
    }

    await onComplete()
  }

  return (
    <Button
      type="button"
      variant="default"
      onClick={handleClick}
      disabled={disabled || isLoading}
      isLoading={isLoading}
    >
      検収完了
    </Button>
  )
}
