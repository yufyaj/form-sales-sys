'use client'

import { useState, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { loginSchema, type LoginFormData } from '@/lib/validations/auth'
import { loginAction } from '@/lib/auth/actions'
import { formatErrorMessage } from '@/lib/utils'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

/**
 * ログインフォームコンポーネント
 * Server Actionsを使用してhttpOnlyクッキーで安全に認証
 */
export default function LoginForm() {
  const router = useRouter()
  const [serverError, setServerError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [attemptCount, setAttemptCount] = useState(0)
  const lastAttemptTime = useRef<number>(0)

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
   * Server Actionを使用してhttpOnlyクッキーで安全にトークンを保存
   */
  const onSubmit = async (data: LoginFormData) => {
    // レート制限: 5回失敗したら1分間待機
    if (attemptCount >= 5) {
      const timeSinceLastAttempt = Date.now() - lastAttemptTime.current
      if (timeSinceLastAttempt < 60000) {
        setServerError('試行回数が多すぎます。しばらく待ってから再度お試しください。')
        return
      }
      setAttemptCount(0)
    }

    setIsLoading(true)
    setServerError('')

    try {
      // Server Actionを使用してログイン処理
      // httpOnlyクッキーで安全にトークンを保存
      const result = await loginAction(data)

      if (!result.success) {
        // 失敗時は試行回数を増やす
        setAttemptCount((prev) => prev + 1)
        lastAttemptTime.current = Date.now()
        setServerError(result.error || '認証に失敗しました')
        return
      }

      // 成功時は試行回数をリセット
      setAttemptCount(0)

      // ダッシュボードへリダイレクト
      router.push('/dashboard')
      router.refresh() // サーバーコンポーネントを再レンダリング
    } catch (error) {
      setAttemptCount((prev) => prev + 1)
      lastAttemptTime.current = Date.now()
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
