'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { loginSchema, type LoginFormData } from '@/lib/validations/auth'
import { apiClient } from '@/lib/api'
import { formatErrorMessage } from '@/lib/utils'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

/**
 * ログインフォームコンポーネント
 * React Hook FormとZodを使用したバリデーション実装
 */
export default function LoginForm() {
  const router = useRouter()
  const [serverError, setServerError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur', // フィールドからフォーカスが外れた時にバリデーション実行
  })

  /**
   * フォーム送信ハンドラー
   */
  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setServerError('')

    try {
      // APIリクエスト
      const response = await apiClient.login(data)

      // トークンをlocalStorageに保存（本番環境ではhttpOnlyクッキーを推奨）
      if (typeof window !== 'undefined') {
        localStorage.setItem('authToken', response.token)
      }

      // ダッシュボードへリダイレクト
      router.push('/dashboard')
    } catch (error) {
      setServerError(formatErrorMessage(error))
    } finally {
      setIsLoading(false)
    }
  }

  return (
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

      {/* メールアドレス入力 */}
      <Input
        label="メールアドレス"
        type="email"
        autoComplete="email"
        error={errors.email?.message}
        {...register('email')}
      />

      {/* パスワード入力 */}
      <Input
        label="パスワード"
        type="password"
        autoComplete="current-password"
        error={errors.password?.message}
        {...register('password')}
      />

      {/* パスワードリセットリンク */}
      <div className="flex items-center justify-end">
        <Link
          href="/reset-password"
          className="text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          パスワードをお忘れですか？
        </Link>
      </div>

      {/* ログインボタン */}
      <Button
        type="submit"
        className="w-full"
        isLoading={isLoading}
        disabled={isLoading}
      >
        {isLoading ? 'ログイン中...' : 'ログイン'}
      </Button>
    </form>
  )
}
