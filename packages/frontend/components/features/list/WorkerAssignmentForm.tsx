'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import {
  assignmentSchema,
  type AssignmentFormData,
} from '@/lib/validations/assignment'
import { formatErrorMessage } from '@/lib/utils'
import type { User } from '@/types/user'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'

export interface WorkerAssignmentFormProps {
  /**
   * プロジェクトID
   */
  projectId: number
  /**
   * リストID
   */
  listId: number
  /**
   * アクティブなワーカー一覧
   */
  workers: User[]
  /**
   * フォーム送信時のコールバック
   */
  onSubmit: (data: AssignmentFormData) => Promise<void>
  /**
   * キャンセル時のコールバック（オプション）
   */
  onCancel?: () => void
  /**
   * ローディング状態（オプション）
   */
  isLoading?: boolean
}

/**
 * ワーカー割り当てフォームコンポーネント
 * リストに対してワーカーを割り当てる際に使用
 */
export default function WorkerAssignmentForm({
  projectId,
  listId,
  workers,
  onSubmit,
  onCancel,
  isLoading: externalIsLoading = false,
}: WorkerAssignmentFormProps) {
  const router = useRouter()
  const [serverError, setServerError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AssignmentFormData>({
    resolver: zodResolver(assignmentSchema),
    mode: 'onBlur',
    defaultValues: {
      priority: 'medium',
      hideAssigned: false,
    },
  })

  /**
   * フォーム送信ハンドラー
   */
  const handleFormSubmit = async (data: AssignmentFormData) => {
    setIsLoading(true)
    setServerError('')

    try {
      await onSubmit(data)
      // 成功時は前の画面に戻る
      router.back()
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

  const loading = isLoading || externalIsLoading

  // ワーカー選択肢を作成
  const workerOptions = workers.map((worker) => ({
    value: worker.id,
    label: worker.full_name,
  }))

  // 優先度選択肢
  const priorityOptions = [
    { value: 'low', label: '低' },
    { value: 'medium', label: '中' },
    { value: 'high', label: '高' },
    { value: 'urgent', label: '緊急' },
  ]

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      className="space-y-6"
      noValidate
    >
      {/* サーバーエラー表示 */}
      {serverError && (
        <div
          className="rounded-md bg-red-50 p-4 text-sm text-red-800"
          role="alert"
        >
          {serverError}
        </div>
      )}

      {/* ワーカー選択 */}
      <Select
        label="ワーカー"
        placeholder="ワーカーを選択してください"
        options={workerOptions}
        error={errors.workerId?.message}
        {...register('workerId', { valueAsNumber: true })}
      />

      {/* 開始行・終了行 */}
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="開始行"
          type="number"
          min={1}
          placeholder="1"
          error={errors.startRow?.message}
          {...register('startRow', { valueAsNumber: true })}
        />

        <Input
          label="終了行"
          type="number"
          min={1}
          placeholder="100"
          error={errors.endRow?.message}
          {...register('endRow', { valueAsNumber: true })}
        />
      </div>

      {/* 優先度 */}
      <Select
        label="優先度"
        options={priorityOptions}
        error={errors.priority?.message}
        {...register('priority')}
      />

      {/* 期限 */}
      <Input
        label="期限（任意）"
        type="date"
        error={errors.dueDate?.message}
        {...register('dueDate')}
      />

      {/* 割り当て済み企業を非表示 */}
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="hideAssigned"
          className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-2 focus:ring-primary"
          {...register('hideAssigned')}
        />
        <label
          htmlFor="hideAssigned"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          割り当て済み企業を非表示
        </label>
      </div>

      {/* ボタン */}
      <div className="flex gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={handleCancel}
          disabled={loading}
          className="flex-1"
        >
          キャンセル
        </Button>
        <Button
          type="submit"
          className="flex-1"
          isLoading={loading}
          disabled={loading}
        >
          {loading ? '割り当て中...' : '割り当て'}
        </Button>
      </div>
    </form>
  )
}
