'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

export interface ListDuplicateDialogProps {
  /**
   * ダイアログの開閉状態
   */
  open: boolean
  /**
   * ダイアログを閉じる際のコールバック
   */
  onOpenChange: (open: boolean) => void
  /**
   * 複製元のリスト名
   */
  originalListName: string
  /**
   * 複製実行時のコールバック
   */
  onDuplicate: (newName: string) => Promise<void>
}

/**
 * リスト複製ダイアログコンポーネント
 */
export default function ListDuplicateDialog({
  open,
  onOpenChange,
  originalListName,
  onDuplicate,
}: ListDuplicateDialogProps) {
  const [newName, setNewName] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  /**
   * ダイアログが開かれた時の初期化処理
   */
  useEffect(() => {
    if (open) {
      // ダイアログが開かれた時、デフォルト名を設定
      setNewName(`${originalListName}のコピー`)
      setError('')
      setIsSubmitting(false)
    }
  }, [open, originalListName])

  /**
   * ダイアログの開閉状態変更処理
   */
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      // ダイアログが閉じられた時、状態をリセット
      setNewName('')
      setError('')
      setIsSubmitting(false)
    }
    onOpenChange(newOpen)
  }

  /**
   * ユーザーフレンドリーなエラーメッセージを取得
   * バックエンドエラーの詳細を隠蔽し、情報漏洩を防ぐ
   */
  const getErrorMessage = (error: unknown): string => {
    const errorMessages: Record<string, string> = {
      'List name already exists': 'このリスト名は既に使用されています',
      'List not found': 'リストが見つかりませんでした',
      'Unauthorized': '権限がありません',
      'Forbidden': 'この操作は許可されていません',
      'Network Error': 'ネットワークエラーが発生しました',
    }

    if (error instanceof Error) {
      return errorMessages[error.message] || 'リストの複製に失敗しました'
    }
    return 'リストの複製に失敗しました'
  }

  /**
   * 複製実行処理
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // トリミング処理
    const trimmedName = newName.trim()

    // バリデーション: 空文字チェック
    if (!trimmedName) {
      setError('リスト名を入力してください')
      return
    }

    // バリデーション: 文字数制限チェック
    if (trimmedName.length > 255) {
      setError('リスト名は255文字以内で入力してください')
      return
    }

    // サニタイゼーション: 制御文字の除去（XSS対策、データ汚染防止）
    const sanitizedName = trimmedName.replace(/[\x00-\x1F\x7F-\x9F]/g, '')

    // バリデーション: サニタイズ後の空文字チェック
    if (!sanitizedName) {
      setError('リスト名に使用できない文字が含まれています')
      return
    }

    try {
      setIsSubmitting(true)
      setError('')
      await onDuplicate(sanitizedName)
      // 成功時のみダイアログを閉じる
      onOpenChange(false)
    } catch (err) {
      // エラー時はダイアログを閉じない
      // バックエンドエラーの詳細を隠蔽し、ユーザーフレンドリーなメッセージを表示
      setError(getErrorMessage(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>リストを複製</DialogTitle>
            <DialogDescription>
              「{originalListName}」を複製します。新しいリスト名を入力してください。
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <Input
              label="新しいリスト名"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              error={error}
              placeholder="リスト名を入力"
              disabled={isSubmitting}
              autoFocus
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={isSubmitting}
            >
              キャンセル
            </Button>
            <Button type="submit" isLoading={isSubmitting} disabled={isSubmitting}>
              複製
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
