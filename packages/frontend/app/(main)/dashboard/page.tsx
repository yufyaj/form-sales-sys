import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ダッシュボード | フォーム営業支援システム',
  description: 'フォーム営業活動の概要とプロジェクト管理',
}

/**
 * ダッシュボードページ
 * ログイン後のホーム画面
 */
export default function DashboardPage() {
  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
          ダッシュボード
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          フォーム営業支援システムへようこそ
        </p>
      </div>

      {/* サンプルカード */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">プロジェクト</h2>
          <p className="mt-2 text-3xl font-bold text-blue-600">0</p>
          <p className="mt-1 text-sm text-gray-500">進行中のプロジェクト</p>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">リスト</h2>
          <p className="mt-2 text-3xl font-bold text-green-600">0</p>
          <p className="mt-1 text-sm text-gray-500">登録済みリスト</p>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">送信済み</h2>
          <p className="mt-2 text-3xl font-bold text-purple-600">0</p>
          <p className="mt-1 text-sm text-gray-500">今月の送信数</p>
        </div>
      </div>
    </div>
  )
}
