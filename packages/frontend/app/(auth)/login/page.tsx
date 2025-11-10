import type { Metadata } from 'next'
import Card, { CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import LoginForm from '@/components/features/auth/LoginForm'

export const metadata: Metadata = {
  title: 'ログイン | フォーム営業支援システム',
  description: 'フォーム営業支援システムへのログイン',
}

/**
 * ログインページ
 * モダンで洗練されたデザイン
 */
export default function LoginPage() {
  return (
    <div className="space-y-6">
      {/* ロゴとタイトル */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-neutral-900 to-neutral-600 dark:from-neutral-100 dark:to-neutral-400 bg-clip-text text-transparent">
          フォーム営業支援システム
        </h1>
        <p className="text-sm text-muted-foreground">
          アカウントにログインしてください
        </p>
      </div>

      {/* ログインカード */}
      <Card animate className="border-neutral-200 dark:border-neutral-800">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-semibold tracking-tight">
            ログイン
          </CardTitle>
          <CardDescription>
            メールアドレスとパスワードを入力してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LoginForm />
        </CardContent>
      </Card>

      {/* フッター */}
      <p className="text-center text-xs text-muted-foreground">
        © 2025 フォーム営業支援システム. All rights reserved.
      </p>
    </div>
  )
}
