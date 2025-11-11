'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion } from 'framer-motion'
import {
  updateClientOrganizationSchema,
  type UpdateClientOrganizationFormData,
} from '@/lib/validations/customer'
import type { ClientOrganization } from '@/types/customer'
import { staggerContainer, staggerItem } from '@/lib/motion'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

interface CustomerFormProps {
  customer?: ClientOrganization // 編集時は既存データを渡す
  onSubmit: (data: UpdateClientOrganizationFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

/**
 * 顧客登録・編集フォームコンポーネント
 *
 * React Hook Form + Zodを使用したバリデーション
 */
export default function CustomerForm({
  customer,
  onSubmit,
  onCancel,
  isLoading = false,
}: CustomerFormProps) {
  const [serverError, setServerError] = useState<string>('')
  const isEditMode = !!customer

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<UpdateClientOrganizationFormData>({
    resolver: zodResolver(updateClientOrganizationSchema),
    mode: 'onBlur', // フォーカスが外れた時にバリデーション実行
    defaultValues: customer
      ? {
          industry: customer.industry || '',
          employeeCount: customer.employeeCount || undefined,
          annualRevenue: customer.annualRevenue || undefined,
          establishedYear: customer.establishedYear || undefined,
          website: customer.website || '',
          salesPerson: customer.salesPerson || '',
          notes: customer.notes || '',
        }
      : {},
  })

  // customer が変更された場合、フォームをリセット
  useEffect(() => {
    if (customer) {
      reset({
        industry: customer.industry || '',
        employeeCount: customer.employeeCount || undefined,
        annualRevenue: customer.annualRevenue || undefined,
        establishedYear: customer.establishedYear || undefined,
        website: customer.website || '',
        salesPerson: customer.salesPerson || '',
        notes: customer.notes || '',
      })
    }
  }, [customer, reset])

  const handleFormSubmit = async (data: UpdateClientOrganizationFormData) => {
    setServerError('')

    try {
      await onSubmit(data)
    } catch (error) {
      setServerError(
        error instanceof Error ? error.message : 'エラーが発生しました'
      )
    }
  }

  const MotionForm = motion.form as any
  const MotionDiv = motion.div as any

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

      {/* 編集モードの場合は顧客名を表示（読み取り専用） */}
      {isEditMode && (
        <MotionDiv variants={staggerItem}>
          <div className="rounded-lg bg-gray-50 p-4">
            <label className="block text-sm font-medium text-gray-700">
              顧客名
            </label>
            <p className="mt-1 text-base font-semibold text-gray-900">
              {customer.organizationName}
            </p>
          </div>
        </MotionDiv>
      )}

      {/* 業種 */}
      <MotionDiv variants={staggerItem}>
        <Input
          label="業種"
          type="text"
          placeholder="例: 製造業、IT・通信、サービス業"
          error={errors.industry?.message}
          {...register('industry')}
        />
      </MotionDiv>

      {/* 従業員数 */}
      <MotionDiv variants={staggerItem}>
        <Input
          label="従業員数"
          type="number"
          placeholder="例: 100"
          error={errors.employeeCount?.message}
          {...register('employeeCount', { valueAsNumber: true })}
        />
        <p className="mt-1 text-xs text-gray-500">人数を半角数字で入力してください</p>
      </MotionDiv>

      {/* 年商 */}
      <MotionDiv variants={staggerItem}>
        <Input
          label="年商（円）"
          type="number"
          placeholder="例: 100000000"
          error={errors.annualRevenue?.message}
          {...register('annualRevenue', { valueAsNumber: true })}
        />
        <p className="mt-1 text-xs text-gray-500">金額を半角数字で入力してください</p>
      </MotionDiv>

      {/* 設立年 */}
      <MotionDiv variants={staggerItem}>
        <Input
          label="設立年"
          type="number"
          placeholder="例: 2000"
          error={errors.establishedYear?.message}
          {...register('establishedYear', { valueAsNumber: true })}
        />
        <p className="mt-1 text-xs text-gray-500">西暦を半角数字で入力してください</p>
      </MotionDiv>

      {/* Webサイト */}
      <MotionDiv variants={staggerItem}>
        <Input
          label="Webサイト"
          type="url"
          placeholder="https://example.com"
          error={errors.website?.message}
          {...register('website')}
        />
      </MotionDiv>

      {/* 担当営業 */}
      <MotionDiv variants={staggerItem}>
        <Input
          label="担当営業"
          type="text"
          placeholder="例: 山田 太郎"
          error={errors.salesPerson?.message}
          {...register('salesPerson')}
        />
      </MotionDiv>

      {/* 備考 */}
      <MotionDiv variants={staggerItem}>
        <label
          htmlFor="notes"
          className="block text-sm font-medium text-gray-700"
        >
          備考
        </label>
        <textarea
          id="notes"
          rows={4}
          placeholder="その他の情報や特記事項を入力してください"
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          {...register('notes')}
        />
        {errors.notes && (
          <p className="mt-1 text-sm text-red-600">{errors.notes.message}</p>
        )}
      </MotionDiv>

      {/* フォームアクション */}
      <MotionDiv
        className="flex items-center justify-end gap-3 pt-4"
        variants={staggerItem}
      >
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
        >
          キャンセル
        </Button>
        <Button type="submit" isLoading={isLoading} disabled={isLoading}>
          {isLoading
            ? isEditMode
              ? '更新中...'
              : '登録中...'
            : isEditMode
              ? '更新'
              : '登録'}
        </Button>
      </MotionDiv>
    </MotionForm>
  )
}
