/**
 * 営業支援会社担当者登録・編集フォーム
 */

'use client'

import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { userCreateSchema, userUpdateSchema, type UserCreateFormData, type UserUpdateFormData } from '@/lib/validations/user'
import { createUser, updateUser } from '@/lib/actions/users'
import { User } from '@/types/user'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

interface StaffFormProps {
  organizationId: number
  user?: User
  onSuccess?: () => void
  onCancel?: () => void
}

export function StaffForm({ organizationId, user, onSuccess, onCancel }: StaffFormProps) {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const isEditMode = !!user

  // 編集モードと新規作成モードで異なるフォームを使用
  const createForm = useForm<UserCreateFormData>({
    resolver: zodResolver(userCreateSchema),
    mode: 'onBlur',
    defaultValues: {
      email: '',
      full_name: '',
      password: '',
      password_confirmation: '',
      phone: '',
      description: '',
    },
  })

  const updateForm = useForm<UserUpdateFormData>({
    resolver: zodResolver(userUpdateSchema),
    mode: 'onBlur',
    defaultValues: user
      ? {
          email: user.email,
          full_name: user.full_name,
          phone: user.phone || '',
          description: user.description || '',
          is_active: user.is_active,
        }
      : undefined,
  })

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = (isEditMode ? updateForm : createForm) as any

  // ユーザーデータが変更されたらフォームをリセット
  useEffect(() => {
    if (isEditMode && user) {
      reset({
        email: user.email,
        full_name: user.full_name,
        phone: user.phone || '',
        description: user.description || '',
        is_active: user.is_active,
      })
    }
  }, [user, isEditMode, reset])

  const onSubmit = async (data: UserCreateFormData | UserUpdateFormData) => {
    setIsSubmitting(true)
    setError(null)

    try {
      if (isEditMode && user) {
        // 更新処理
        const result = await updateUser(user.id, organizationId, data as UserUpdateFormData)

        if (!result.success) {
          setError(result.error || '更新に失敗しました')
          return
        }

        if (onSuccess) {
          onSuccess()
        } else {
          router.push('/dashboard/sales-company/staff')
          router.refresh()
        }
      } else {
        // 新規作成処理
        const createData = data as UserCreateFormData
        const result = await createUser({
          organization_id: organizationId,
          email: createData.email,
          full_name: createData.full_name,
          password: createData.password,
          phone: createData.phone || null,
          description: createData.description || null,
        })

        if (!result.success) {
          setError(result.error || '作成に失敗しました')
          return
        }

        if (onSuccess) {
          onSuccess()
        } else {
          router.push('/dashboard/sales-company/staff')
          router.refresh()
        }
      }
    } catch (err) {
      console.error('フォーム送信エラー:', err)
      setError('予期しないエラーが発生しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    } else {
      router.back()
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <div className="rounded-md bg-red-50 p-4" role="alert">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <Input
        label="メールアドレス"
        type="email"
        required
        error={errors.email?.message}
        {...register('email')}
      />

      <Input
        label="氏名"
        type="text"
        required
        error={errors.full_name?.message}
        {...register('full_name')}
      />

      {!isEditMode && (
        <>
          <Input
            label="パスワード"
            type="password"
            required
            error={errors.password?.message}
            helperText="12文字以上、大文字・小文字・数字を含む"
            {...register('password')}
          />

          <Input
            label="パスワード（確認）"
            type="password"
            required
            error={(errors as any).password_confirmation?.message}
            {...register('password_confirmation' as any)}
          />
        </>
      )}

      <Input
        label="電話番号"
        type="tel"
        error={errors.phone?.message}
        {...register('phone')}
      />

      <div className="space-y-2">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          備考
        </label>
        <textarea
          id="description"
          rows={4}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          {...register('description')}
        />
        {errors.description && (
          <p className="text-sm text-red-600">{errors.description.message}</p>
        )}
      </div>

      {isEditMode && (
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="is_active"
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            {...register('is_active')}
          />
          <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
            アクティブ
          </label>
        </div>
      )}

      <div className="flex justify-end space-x-4">
        <Button
          type="button"
          variant="outline"
          onClick={handleCancel}
          disabled={isSubmitting}
        >
          キャンセル
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? '処理中...' : isEditMode ? '更新' : '登録'}
        </Button>
      </div>
    </form>
  )
}
