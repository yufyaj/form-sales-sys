/**
 * 営業支援会社担当者新規登録画面
 */

import Link from 'next/link'
import { StaffForm } from '@/components/features/staff/StaffForm'
import { Button } from '@/components/ui/Button'

// TODO: 認証コンテキストから組織IDを取得
const TEMP_ORGANIZATION_ID = 1

export const metadata = {
  title: '担当者追加 | 営業支援システム',
  description: '新しい担当者を登録',
}

export default function NewStaffPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-6">
        <Link href="/dashboard/sales-company/staff">
          <Button variant="outline" size="sm">
            ← 一覧に戻る
          </Button>
        </Link>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">担当者の新規登録</h1>
        <StaffForm organizationId={TEMP_ORGANIZATION_ID} />
      </div>
    </div>
  )
}
