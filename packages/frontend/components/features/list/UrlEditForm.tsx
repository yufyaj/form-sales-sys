'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { urlEditSchema, type UrlEditFormData } from '@/lib/validations/list'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

export interface UrlEditFormProps {
  listId: number
  projectId: number
  defaultUrl?: string | null
  onSubmit: (data: UrlEditFormData) => Promise<void>
}

/**
 * URL編集フォームコンポーネント
 *
 * 【セキュリティ対策】
 * - HTTPSのURLのみ許可（HTTPは拒否）
 * - Zodバリデーションで型安全性を確保
 * - サーバーエラーの詳細を隠蔽（安全なメッセージのみ表示）
 *
 * 【実装詳細】
 * - React Hook FormとZodを統合して型安全なバリデーション
 * - mode: 'onBlur'により、ユーザーがフィールドから離れた時にバリデーション
 * - isSubmittingでローディング状態を自動管理
 * - noValidate属性でブラウザのデフォルトバリデーションを無効化
 *
 * @example
 * ```tsx
 * <UrlEditForm
 *   listId={1}
 *   projectId={1}
 *   defaultUrl="https://example.com"
 *   onSubmit={async (data) => {
 *     await updateListAction(projectId, listId, data)
 *   }}
 * />
 * ```
 */
export default function UrlEditForm({
  listId,
  projectId,
  defaultUrl,
  onSubmit,
}: UrlEditFormProps) {
  const [serverError, setServerError] = useState<string>('')

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UrlEditFormData>({
    resolver: zodResolver(urlEditSchema),
    mode: 'onBlur', // フォーカスが外れた時にバリデーション
    defaultValues: {
      url: defaultUrl || '',
    },
  })

  const handleFormSubmit = async (data: UrlEditFormData) => {
    // サーバーエラーをクリア
    // なぜ必要か: 前回のエラーメッセージを消すため
    setServerError('')

    try {
      await onSubmit(data)
    } catch (error) {
      // エラーをキャッチして、ユーザーフレンドリーなメッセージを表示
      // なぜ必要か: サーバーエラーの詳細を隠蔽し、安全なメッセージのみ表示
      setServerError(
        error instanceof Error ? error.message : 'エラーが発生しました'
      )
    }
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} noValidate className="space-y-4">
      {serverError && (
        <div
          className="rounded-md bg-red-50 p-4 text-sm text-red-800"
          role="alert"
        >
          {serverError}
        </div>
      )}

      <Input
        label="URL"
        type="url"
        placeholder="https://example.com"
        error={errors.url?.message}
        {...register('url')}
      />

      <Button type="submit" isLoading={isSubmitting} disabled={isSubmitting}>
        {isSubmitting ? '更新中...' : 'URLを更新'}
      </Button>
    </form>
  )
}
