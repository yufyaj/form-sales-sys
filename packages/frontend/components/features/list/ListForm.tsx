'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { listSchema, type ListFormData } from '@/lib/validations/list'
import { formatErrorMessage } from '@/lib/utils'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

export interface ListFormProps {
  /**
   * プロジェクトID
   */
  projectId: number
  /**
   * 既存リストの初期値（編集時に使用）
   */
  defaultValues?: Partial<ListFormData>
  /**
   * フォーム送信時のコールバック
   */
  onSubmit: (data: ListFormData) => Promise<void>
  /**
   * キャンセル時のコールバック（オプション）
   */
  onCancel?: () => void
  /**
   * 編集モード（既存リストの編集か新規作成か）
   */
  isEditMode?: boolean
}

/**
 * リストフォームコンポーネント
 * リストの新規作成・編集に使用
 */
export default function ListForm({
  projectId,
  defaultValues,
  onSubmit,
  onCancel,
  isEditMode = false,
}: ListFormProps) {
  const router = useRouter()
  const [serverError, setServerError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ListFormData>({
    resolver: zodResolver(listSchema),
    mode: 'onBlur',
    defaultValues: defaultValues || {},
  })

  /**
   * フォーム送信ハンドラー
   */
  const handleFormSubmit = async (data: ListFormData) => {
    setIsLoading(true)
    setServerError('')

    try {
      await onSubmit(data)
      // 成功時はリスト一覧画面にリダイレクト
      router.push(`/projects/${projectId}/lists`)
      router.refresh()
    } catch (error) {
      setServerError(formatErrorMessage(error))
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * キャンセルハンドラー
   */
  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    } else {
      router.back()
    }
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6" noValidate>
      {/* サーバーエラー表示 */}
      {serverError && (
        <div
          className="rounded-md bg-red-50 p-4 text-sm text-red-800"
          role="alert"
        >
          {serverError}
        </div>
      )}

      {/* リスト名 */}
      <Input
        label="リスト名"
        type="text"
        placeholder="例：新規営業先リスト"
        error={errors.name?.message}
        {...register('name')}
      />

      {/* 説明 */}
      <div className="w-full space-y-2">
        <label
          htmlFor="description"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          説明（任意）
        </label>
        <textarea
          id="description"
          rows={5}
          placeholder="リストの詳細説明を入力してください"
          className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-base"
          {...register('description')}
        />
        {errors.description?.message && (
          <p className="text-sm font-medium text-destructive" role="alert">
            {errors.description.message}
          </p>
        )}
      </div>

      {/* ボタン */}
      <div className="flex gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={handleCancel}
          disabled={isLoading}
          className="flex-1"
        >
          キャンセル
        </Button>
        <Button
          type="submit"
          className="flex-1"
          isLoading={isLoading}
          disabled={isLoading}
        >
          {isLoading
            ? isEditMode
              ? '更新中...'
              : '作成中...'
            : isEditMode
            ? 'リストを更新'
            : 'リストを作成'}
        </Button>
      </div>
    </form>
  )
}
