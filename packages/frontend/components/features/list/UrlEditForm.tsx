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
 * セキュリティ: HTTPSのURLのみ許可
 *
 * @example
 * ```tsx
 * <UrlEditForm
 *   listId={1}
 *   projectId={1}
 *   defaultUrl="https://example.com"
 *   onSubmit={handleSubmit}
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
    setServerError('')
    try {
      await onSubmit(data)
    } catch (error) {
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
