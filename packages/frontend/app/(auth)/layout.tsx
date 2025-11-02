/**
 * 認証関連ページのレイアウト
 * ログイン前のページで使用（ログイン、パスワードリセット等）
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">{children}</div>
    </div>
  )
}
