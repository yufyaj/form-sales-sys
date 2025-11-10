/**
 * 認証関連ページのレイアウト
 * モダンなデザインで統一されたログイン前のページレイアウト
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="relative flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      {/* グラデーション背景 */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-neutral-50 via-neutral-100 to-neutral-50 dark:from-neutral-950 dark:via-neutral-900 dark:to-neutral-950" />

      {/* グリッドパターン（装飾） */}
      <div
        className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]"
        aria-hidden="true"
      />

      {/* グラデーションオーバーレイ（上部） */}
      <div
        className="absolute left-1/2 top-0 -z-10 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-br from-primary-500/20 to-primary-600/20 blur-3xl"
        aria-hidden="true"
      />

      {/* コンテンツ */}
      <div className="w-full max-w-md space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-slow">
        {children}
      </div>
    </div>
  )
}
