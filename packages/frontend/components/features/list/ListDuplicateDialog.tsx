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
   * 複製実行処理
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // バリデーション
    if (!newName.trim()) {
      setError('リスト名を入力してください')
      return
    }

    if (newName.length > 255) {
      setError('リスト名は255文字以内で入力してください')
      return
    }

    try {
      setIsSubmitting(true)
      setError('')
      await onDuplicate(newName)
      // 成功時のみダイアログを閉じる
      onOpenChange(false)
    } catch (err) {
      // エラー時はダイアログを閉じない
      setError(
        err instanceof Error ? err.message : 'リストの複製に失敗しました'
      )
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
