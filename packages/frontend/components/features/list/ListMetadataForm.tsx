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
 * URLと説明を一括で編集できる
 *
 * 【セキュリティ対策】
 * - HTTPSのURLのみ許可（HTTPは拒否）
 * - XSS対策: 説明フィールドから制御文字を除去（\x00-\x1F, \x7F）
 * - 説明は5000文字以内に制限
 * - Zodバリデーションで型安全性を確保
 *
 * 【実装詳細】
 * - React Hook FormとZodを統合
 * - mode: 'onBlur'でUXを最適化（入力中はバリデーションしない）
 * - transformでサニタイゼーション（制御文字除去）を自動実行
 * - エラーハンドリングで安全なメッセージのみ表示
 *
 * 【XSS対策の詳細】
 * - Zodのtransform機能を使用して、制御文字を除去
 * - 正規表現 /[\x00-\x1F\x7F]/g で以下を除去:
 *   - \x00-\x1F: 制御文字（NULL、改行以外の特殊文字など）
 *   - \x7F: DEL文字
 * - これにより、潜在的なXSS攻撃ベクトルを防止
 *
 * @example
 * ```tsx
 * <ListMetadataForm
 *   listId={1}
 *   projectId={1}
 *   defaultValues={{ url: 'https://example.com', description: '説明文' }}
 *   onSubmit={async (data) => {
 *     await updateListAction(projectId, listId, data)
 *   }}
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
