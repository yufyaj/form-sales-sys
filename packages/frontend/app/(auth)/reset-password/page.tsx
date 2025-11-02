import Card, { CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import ResetPasswordForm from '@/components/features/auth/ResetPasswordForm'

/**
 * パスワードリセットページ
 */
export default function ResetPasswordPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-center">パスワードリセット</CardTitle>
      </CardHeader>
      <CardContent>
        <ResetPasswordForm />
      </CardContent>
    </Card>
  )
}
