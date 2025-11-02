import Card, { CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import LoginForm from '@/components/features/auth/LoginForm'

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
