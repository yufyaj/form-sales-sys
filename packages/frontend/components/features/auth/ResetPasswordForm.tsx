'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { resetPasswordSchema, type ResetPasswordFormData } from '@/lib/validations/auth'
import { requestPasswordResetAction } from '@/lib/auth/actions'
import { formatErrorMessage } from '@/lib/utils'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

/**
 * パスワードリセットフォームコンポーネント
 * Server Actionsを使用してリセットリンクを送信
 */
export default function ResetPasswordForm() {
  const [serverError, setServerError] = useState<string>('')
  const [successMessage, setSuccessMessage] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    mode: 'onBlur',
  })

  /**
   * フォーム送信ハンドラー
   * Server Actionを使用してリセットリクエストを送信
   */
  const onSubmit = async (data: ResetPasswordFormData) => {
    setIsLoading(true)
    setServerError('')
    setSuccessMessage('')

    try {
      // Server Actionを使用してパスワードリセットリクエスト
      const result = await requestPasswordResetAction(data)

      if (!result.success) {
        setServerError(result.error || 'リクエストに失敗しました')
        return
      }

      setSuccessMessage(
        result.message || 'パスワードリセットリンクをメールで送信しました。'
      )
    } catch (error) {
      setServerError(formatErrorMessage(error))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* 説明文 */}
      <p className="text-sm text-gray-600">
        登録されているメールアドレスを入力してください。パスワードリセット用のリンクをお送りします。
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
        {/* サーバーエラー表示 */}
        {serverError && (
          <div
            className="rounded-md bg-red-50 p-4 text-sm text-red-800"
            role="alert"
          >
            {serverError}
          </div>
        )}

        {/* 成功メッセージ表示 */}
        {successMessage && (
          <div
            className="rounded-md bg-green-50 p-4 text-sm text-green-800"
            role="alert"
          >
            {successMessage}
          </div>
        )}

        {/* メールアドレス入力 */}
        <Input
          label="メールアドレス"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register('email')}
        />

        {/* 送信ボタン */}
        <Button
          type="submit"
          className="w-full"
          isLoading={isLoading}
          disabled={isLoading}
        >
          {isLoading ? '送信中...' : 'リセットリンクを送信'}
        </Button>
      </form>

      {/* ログインページへのリンク */}
      <div className="text-center">
        <Link
          href="/login"
          className="text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          ログインページに戻る
        </Link>
      </div>
    </div>
  )
}
