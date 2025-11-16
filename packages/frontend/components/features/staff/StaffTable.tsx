/**
 * 営業支援会社担当者一覧テーブル
 */

'use client'

import { useState } from 'react'
import { User } from '@/types/user'
import Badge from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { deleteUser } from '@/lib/actions/users'
import { useRouter } from 'next/navigation'

interface StaffTableProps {
  users: User[]
  organizationId: number
  onEdit?: (user: User) => void
}

export function StaffTable({ users, organizationId, onEdit }: StaffTableProps) {
  const router = useRouter()
  const [deletingUserId, setDeletingUserId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleDelete = async (user: User) => {
    if (!confirm(`${user.full_name}さんを削除してもよろしいですか？`)) {
      return
    }

    setDeletingUserId(user.id)
    setError(null)

    try {
      const result = await deleteUser(user.id, organizationId)

      if (!result.success) {
        setError(result.error || '削除に失敗しました')
        return
      }

      router.refresh()
    } catch (err) {
      console.error('削除エラー:', err)
      setError('削除処理中にエラーが発生しました')
    } finally {
      setDeletingUserId(null)
    }
  }

  const handleEdit = (user: User) => {
    if (onEdit) {
      onEdit(user)
    } else {
      router.push(`/dashboard/sales-company/staff/${user.id}/edit`)
    }
  }

  if (users.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">担当者が登録されていません。</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-md bg-red-50 p-4" role="alert">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                氏名
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                メールアドレス
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                電話番号
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                ステータス
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                  {user.description && (
                    <div className="text-sm text-gray-500">{user.description}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{user.email}</div>
                  {user.is_email_verified ? (
                    <div className="text-xs text-green-600">認証済み</div>
                  ) : (
                    <div className="text-xs text-gray-400">未認証</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.phone || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {user.is_active ? (
                    <Badge variant="success">アクティブ</Badge>
                  ) : (
                    <Badge variant="default">無効</Badge>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(user)}
                  >
                    編集
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(user)}
                    disabled={deletingUserId === user.id}
                  >
                    {deletingUserId === user.id ? '削除中...' : '削除'}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
