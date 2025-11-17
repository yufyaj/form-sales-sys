'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { projectSchema, type ProjectFormData, ProjectStatus } from '@/lib/validations/project'
import { formatErrorMessage } from '@/lib/utils'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Select, { type SelectOption } from '@/components/ui/Select'

export interface ProjectFormProps {
  /**
   * 既存プロジェクトの初期値（編集時に使用）
   */
  defaultValues?: Partial<ProjectFormData>
  /**
   * 顧客企業の選択肢
   */
  clientOrganizations: SelectOption[]
  /**
   * フォーム送信時のコールバック
   */
  onSubmit: (data: ProjectFormData) => Promise<void>
  /**
   * キャンセル時のコールバック（オプション）
   */
  onCancel?: () => void
  /**
   * 編集モード（既存プロジェクトの編集か新規作成か）
   */
  isEditMode?: boolean
}

/**
 * プロジェクトフォームコンポーネント
 * プロジェクトの新規作成・編集に使用
 */
export default function ProjectForm({
  defaultValues,
  clientOrganizations,
  onSubmit,
  onCancel,
  isEditMode = false,
}: ProjectFormProps) {
  const router = useRouter()
  const [serverError, setServerError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    mode: 'onBlur',
    defaultValues: defaultValues || {
      status: ProjectStatus.PLANNING,
    },
  })

  /**
   * フォーム送信ハンドラー
   */
  const handleFormSubmit = async (data: ProjectFormData) => {
    setIsLoading(true)
    setServerError('')

    try {
      await onSubmit(data)
      // 成功時はプロジェクト一覧画面にリダイレクト
      router.push('/projects')
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

  // ステータスの選択肢
  const statusOptions: SelectOption[] = [
    { value: ProjectStatus.PLANNING, label: '企画中' },
    { value: ProjectStatus.ACTIVE, label: '進行中' },
    { value: ProjectStatus.COMPLETED, label: '完了' },
    { value: ProjectStatus.CANCELLED, label: 'キャンセル' },
  ]

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

      {/* プロジェクト名 */}
      <Input
        label="プロジェクト名"
        type="text"
        placeholder="例：新規Webサイト構築プロジェクト"
        error={errors.name?.message}
        {...register('name')}
      />

      {/* 顧客企業選択 */}
      <Select
        label="顧客企業"
        options={clientOrganizations}
        placeholder="顧客企業を選択してください"
        error={errors.client_organization_id?.message}
        {...register('client_organization_id', {
          valueAsNumber: true,
        })}
      />

      {/* ステータス */}
      <Select
        label="ステータス"
        options={statusOptions}
        error={errors.status?.message}
        {...register('status')}
      />

      {/* 開始日 */}
      <Input
        label="開始日"
        type="date"
        error={errors.start_date?.message}
        {...register('start_date')}
      />

      {/* 終了日 */}
      <Input
        label="終了日"
        type="date"
        error={errors.end_date?.message}
        {...register('end_date')}
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
          placeholder="プロジェクトの詳細説明を入力してください"
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
            ? 'プロジェクトを更新'
            : 'プロジェクトを作成'}
        </Button>
      </div>
    </form>
  )
}
