/**
 * 営業支援会社担当者編集画面
 */

import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getUser } from '@/lib/actions/users'
import { StaffForm } from '@/components/features/staff/StaffForm'
import { Button } from '@/components/ui/Button'

// TODO: 認証コンテキストから組織IDを取得
const TEMP_ORGANIZATION_ID = 1

interface EditStaffPageProps {
  params: Promise<{
    id: string
  }>
}

export const metadata = {
  title: '担当者編集 | 営業支援システム',
  description: '担当者情報を編集',
}

export default async function EditStaffPage({ params }: EditStaffPageProps) {
  const { id } = await params
  const userId = parseInt(id, 10)

  if (isNaN(userId)) {
    notFound()
  }

  const result = await getUser(userId, TEMP_ORGANIZATION_ID)

  if (!result.success || !result.data) {
    notFound()
  }

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
        <h1 className="text-2xl font-bold text-gray-900 mb-6">担当者情報の編集</h1>
        <StaffForm organizationId={TEMP_ORGANIZATION_ID} user={result.data} />
      </div>
    </div>
  )
}
