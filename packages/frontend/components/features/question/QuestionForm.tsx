'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion } from 'framer-motion'
import {
  createWorkerQuestionSchema,
  type CreateWorkerQuestionFormData,
} from '@/lib/validations/question'
import { createQuestionAction } from '@/lib/actions/questions'
import { staggerContainer, staggerItem } from '@/lib/motion'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

interface QuestionFormProps {
  clientOrganizationId: number
  clientOrganizationName: string
  onSuccess?: () => void
  onCancel?: () => void
}

/**
 * ワーカー質問投稿フォームコンポーネント
 *
 * React Hook Form + Zodを使用したバリデーション
 * Server Actionsでフォーム送信を処理
 */
export default function QuestionForm({
  clientOrganizationId,
  clientOrganizationName,
  onSuccess,
  onCancel,
}: QuestionFormProps) {
  const [serverError, setServerError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string>('')

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateWorkerQuestionFormData>({
    resolver: zodResolver(createWorkerQuestionSchema),
    mode: 'onBlur',
    defaultValues: {
      title: '',
      content: '',
      priority: 'medium',
    },
  })

  const handleFormSubmit = async (data: CreateWorkerQuestionFormData) => {
    setIsLoading(true)
    setServerError('')
    setSuccessMessage('')

    try {
      const result = await createQuestionAction(clientOrganizationId, data)

      if (!result.success) {
        setServerError(result.error)
        return
      }

      // 成功時の処理
      setSuccessMessage('質問を投稿しました')
      reset() // フォームをリセット

      // 成功コールバックを実行
      if (onSuccess) {
        // メッセージ表示後にコールバック実行
        setTimeout(() => {
          onSuccess()
        }, 1000)
      }
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : '予期しないエラーが発生しました'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const MotionForm = motion.form
  const MotionDiv = motion.div

  return (
    <MotionForm
      onSubmit={handleSubmit(handleFormSubmit)}
      className="space-y-6"
      noValidate
      initial="hidden"
      animate="visible"
      variants={staggerContainer}
    >
      {/* サーバーエラー表示 */}
      {serverError && (
        <MotionDiv
          className="rounded-md bg-red-50 p-4 text-sm text-red-800"
          role="alert"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          {serverError}
        </MotionDiv>
      )}

      {/* 成功メッセージ表示 */}
      {successMessage && (
        <MotionDiv
          className="rounded-md bg-green-50 p-4 text-sm text-green-800"
          role="alert"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          {successMessage}
        </MotionDiv>
      )}

      {/* 顧客名表示 */}
      <MotionDiv variants={staggerItem}>
        <div className="rounded-lg bg-gray-50 p-4">
          <label className="block text-sm font-medium text-gray-700">
            質問対象の顧客
          </label>
          <p className="mt-1 text-base font-semibold text-gray-900">
            {clientOrganizationName}
          </p>
        </div>
      </MotionDiv>

      {/* 質問タイトル */}
      <MotionDiv variants={staggerItem}>
        <Input
          label="質問タイトル"
          type="text"
          placeholder="例: フォーム入力の手順について"
          error={errors.title?.message}
          {...register('title')}
          disabled={isLoading}
        />
      </MotionDiv>

      {/* 質問内容 */}
      <MotionDiv variants={staggerItem}>
        <label
          htmlFor="content"
          className="block text-sm font-medium text-gray-700"
        >
          質問内容 <span className="text-red-500">*</span>
        </label>
        <textarea
          id="content"
          rows={6}
          placeholder="質問内容を詳しく入力してください"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          {...register('content')}
          disabled={isLoading}
        />
        {errors.content && (
          <p className="mt-1 text-sm text-red-600">{errors.content.message}</p>
        )}
      </MotionDiv>

      {/* 優先度 */}
      <MotionDiv variants={staggerItem}>
        <label
          htmlFor="priority"
          className="block text-sm font-medium text-gray-700"
        >
          優先度
        </label>
        <select
          id="priority"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          {...register('priority')}
          disabled={isLoading}
        >
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
        </select>
        {errors.priority && (
          <p className="mt-1 text-sm text-red-600">{errors.priority.message}</p>
        )}
      </MotionDiv>

      {/* フォームアクション */}
      <MotionDiv
        className="flex items-center justify-end gap-3 pt-4"
        variants={staggerItem}
      >
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            キャンセル
          </Button>
        )}
        <Button type="submit" isLoading={isLoading} disabled={isLoading}>
          {isLoading ? '投稿中...' : '質問を投稿'}
        </Button>
      </MotionDiv>
    </MotionForm>
  )
}
