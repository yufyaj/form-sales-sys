import type { Metadata } from 'next'
import Card, { CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import LoginForm from '@/components/features/auth/LoginForm'

export const metadata: Metadata = {
  title: 'ログイン | フォーム営業支援システム',
  description: 'フォーム営業支援システムへのログイン',
}

/**
 * ログインページ
 */
export default function LoginPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-center">ログイン</CardTitle>
      </CardHeader>
      <CardContent>
        <LoginForm />
      </CardContent>
    </Card>
  )
}
