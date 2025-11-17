/**
 * 営業支援会社担当者管理画面
 */

import { Suspense } from 'react'
import Link from 'next/link'
import { getUserList } from '@/lib/actions/users'
import { StaffTable } from '@/components/features/staff/StaffTable'
import { Button } from '@/components/ui/Button'

// TODO: 認証コンテキストから組織IDを取得
// 現在は開発用に固定値を使用
const TEMP_ORGANIZATION_ID = 1

export const metadata = {
  title: '担当者管理 | 営業支援システム',
  description: '営業支援会社の担当者一覧',
}

async function StaffListContent() {
  const result = await getUserList(TEMP_ORGANIZATION_ID)

  if (!result.success || !result.data) {
    return (
      <div className="rounded-md bg-red-50 p-4" role="alert">
        <p className="text-sm text-red-800">
          {result.error || 'データの取得に失敗しました'}
        </p>
      </div>
    )
  }

  const { users, total } = result.data

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">担当者一覧</h2>
          <p className="text-sm text-gray-600 mt-1">
            全{total}件の担当者が登録されています
          </p>
        </div>
        <Link href="/dashboard/sales-company/staff/new">
          <Button>担当者を追加</Button>
        </Link>
      </div>

      <StaffTable users={users} organizationId={TEMP_ORGANIZATION_ID} />
    </div>
  )
}

export default function StaffPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <Suspense
        fallback={
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-500">読み込み中...</div>
          </div>
        }
      >
        <StaffListContent />
      </Suspense>
    </div>
  )
}
