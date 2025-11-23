'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { listMetadataSchema, type ListMetadataFormData } from '@/lib/validations/list'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import Button from '@/components/ui/Button'

export interface ListMetadataFormProps {
  listId: number
  projectId: number
  defaultValues?: Partial<ListMetadataFormData>
  onSubmit: (data: ListMetadataFormData) => Promise<void>
}

/**
 * リストメタデータ編集フォームコンポーネント
 * URLと説明を編集できる
 * セキュリティ: HTTPSのURLのみ許可、XSS対策（制御文字除去）
 *
 * @example
 * ```tsx
 * <ListMetadataForm
 *   listId={1}
 *   projectId={1}
 *   defaultValues={{ url: 'https://example.com', description: '説明文' }}
 *   onSubmit={handleSubmit}
 * />
 * ```
 */
export default function ListMetadataForm({
  listId,
  projectId,
  defaultValues,
  onSubmit,
}: ListMetadataFormProps) {
  const [serverError, setServerError] = useState<string>('')

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ListMetadataFormData>({
    resolver: zodResolver(listMetadataSchema),
    mode: 'onBlur',
    defaultValues: {
      url: defaultValues?.url || '',
      description: defaultValues?.description || '',
    },
  })

  const handleFormSubmit = async (data: ListMetadataFormData) => {
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

      <Textarea
        label="説明"
        placeholder="リストの説明を入力してください"
        rows={5}
        error={errors.description?.message}
        {...register('description')}
      />

      <Button type="submit" isLoading={isSubmitting} disabled={isSubmitting}>
        {isSubmitting ? '更新中...' : '更新'}
      </Button>
    </form>
  )
}
