'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Trash2, Globe } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import type { NgListDomain } from '@/types/ngListDomain'
import { deleteNgListDomain } from '@/lib/api/ngListDomains'
import { transitions } from '@/lib/motion'

interface NgListDomainTableProps {
  ngDomains: NgListDomain[]
  onDelete?: () => void
}

/**
 * NGリストドメイン一覧テーブルコンポーネント
 */
export function NgListDomainTable({ ngDomains, onDelete }: NgListDomainTableProps) {
  const [deletingId, setDeletingId] = useState<number | null>(null)

  /**
   * NGドメイン削除ハンドラ
   */
  const handleDelete = async (id: number, domain: string) => {
    if (!confirm(`NGドメイン "${domain}" を削除してもよろしいですか?`)) {
      return
    }

    setDeletingId(id)

    try {
      await deleteNgListDomain(id)
      onDelete?.()
    } catch (err) {
      console.error('NGドメイン削除エラー:', err)
      alert('削除に失敗しました。もう一度お試しください。')
    } finally {
      setDeletingId(null)
    }
  }

  /**
   * 日時のフォーマット
   */
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (ngDomains.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-12 text-center">
        <Globe className="mx-auto h-12 w-12 text-muted-foreground/50" />
        <p className="mt-4 text-sm text-muted-foreground">
          NGドメインが登録されていません
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                ドメイン
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                タイプ
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                メモ
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                登録日時
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                アクション
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {ngDomains.map((ngDomain) => (
              <motion.tr
                key={ngDomain.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={transitions.fast}
                layout
              >
                <td className="whitespace-nowrap px-6 py-4">
                  <code className="rounded bg-muted px-2 py-1 text-sm font-mono">
                    {ngDomain.domain}
                  </code>
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  {ngDomain.isWildcard ? (
                    <Badge variant="info">ワイルドカード</Badge>
                  ) : (
                    <Badge variant="default">完全一致</Badge>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="max-w-md truncate text-sm text-muted-foreground">
                    {ngDomain.memo || '-'}
                  </div>
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <span className="text-sm text-muted-foreground">
                    {formatDate(ngDomain.createdAt)}
                  </span>
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(ngDomain.id, ngDomain.domain)}
                    disabled={deletingId === ngDomain.id}
                    className="text-destructive hover:bg-destructive/10"
                  >
                    {deletingId === ngDomain.id ? (
                      '削除中...'
                    ) : (
                      <>
                        <Trash2 className="h-4 w-4" />
                        削除
                      </>
                    )}
                  </Button>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
