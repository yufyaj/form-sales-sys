'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Table, { Column } from '@/components/ui/Table'
import Button from '@/components/ui/Button'
import { List } from '@/lib/api/lists'
import ListDuplicateDialog from './ListDuplicateDialog'

export interface ListTableProps {
  /**
   * プロジェクトID
   */
  projectId: number
  /**
   * リスト一覧データ
   */
  lists: List[]
  /**
   * ローディング状態
   */
  isLoading?: boolean
  /**
   * 新規作成ボタンクリック時のコールバック
   */
  onCreateClick?: () => void
  /**
   * CSVインポートボタンクリック時のコールバック
   */
  onImportClick?: () => void
  /**
   * 削除ボタンクリック時のコールバック
   */
  onDeleteClick?: (listId: number) => Promise<void>
  /**
   * 複製ボタンクリック時のコールバック
   */
  onDuplicateClick?: (listId: number, newName: string) => Promise<void>
}

/**
 * リスト一覧テーブルコンポーネント
 */
export default function ListTable({
  projectId,
  lists,
  isLoading = false,
  onCreateClick,
  onImportClick,
  onDeleteClick,
  onDuplicateClick,
}: ListTableProps) {
  const router = useRouter()
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false)
  const [duplicatingList, setDuplicatingList] = useState<List | null>(null)

  /**
   * 日付のフォーマット
   */
  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  }

  /**
   * 行クリック時の処理
   */
  const handleRowClick = (list: List) => {
    router.push(`/projects/${projectId}/lists/${list.id}`)
  }

  /**
   * 編集ボタンクリック時の処理
   */
  const handleEditClick = (e: React.MouseEvent, listId: number) => {
    e.stopPropagation() // 行クリックイベントの伝播を止める
    router.push(`/projects/${projectId}/lists/${listId}/edit`)
  }

  /**
   * 削除ボタンクリック時の処理
   */
  const handleDeleteClick = async (e: React.MouseEvent, listId: number) => {
    e.stopPropagation() // 行クリックイベントの伝播を止める

    if (!onDeleteClick) return

    if (!confirm('このリストを削除してもよろしいですか？')) {
      return
    }

    try {
      setDeletingId(listId)
      await onDeleteClick(listId)
    } finally {
      setDeletingId(null)
    }
  }

  /**
   * 複製ボタンクリック時の処理
   */
  const handleDuplicateClick = (e: React.MouseEvent, list: List) => {
    e.stopPropagation() // 行クリックイベントの伝播を止める
    setDuplicatingList(list)
    setDuplicateDialogOpen(true)
  }

  /**
   * 複製実行処理
   */
  const handleDuplicate = async (newName: string) => {
    if (!onDuplicateClick || !duplicatingList) return
    await onDuplicateClick(duplicatingList.id, newName)
  }

  /**
   * テーブルのカラム定義
   */
  const columns: Column<List>[] = [
    {
      key: 'name',
      header: 'リスト名',
      align: 'left',
    },
    {
      key: 'description',
      header: '説明',
      align: 'left',
      render: (list: List) => list.description || '-',
    },
    {
      key: 'created_at',
      header: '作成日',
      align: 'center',
      render: (list: List) => formatDate(list.created_at),
    },
    {
      key: 'actions',
      header: '操作',
      align: 'center',
      render: (list: List) => (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => handleEditClick(e, list.id)}
          >
            編集
          </Button>
          {onDuplicateClick && (
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => handleDuplicateClick(e, list)}
              aria-label={`${list.name}を複製`}
            >
              複製
            </Button>
          )}
          {onDeleteClick && (
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => handleDeleteClick(e, list.id)}
              disabled={deletingId === list.id}
              className="text-red-600 hover:bg-red-50 hover:text-red-700"
            >
              {deletingId === list.id ? '削除中...' : '削除'}
            </Button>
          )}
        </div>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
          <p className="mt-4 text-sm text-muted-foreground">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">リスト一覧</h2>
          <p className="text-sm text-muted-foreground">
            全{lists.length}件のリスト
          </p>
        </div>
        <div className="flex gap-3">
          {onImportClick && (
            <Button variant="outline" onClick={onImportClick}>
              CSVインポート
            </Button>
          )}
          {onCreateClick && (
            <Button onClick={onCreateClick}>新規リスト作成</Button>
          )}
        </div>
      </div>

      {/* テーブル */}
      <Table
        columns={columns}
        data={lists}
        keyExtractor={(list) => list.id.toString()}
        onRowClick={handleRowClick}
        emptyMessage="リストがありません。新規作成してください。"
      />

      {/* 複製ダイアログ */}
      {duplicatingList && (
        <ListDuplicateDialog
          open={duplicateDialogOpen}
          onOpenChange={setDuplicateDialogOpen}
          originalListName={duplicatingList.name}
          onDuplicate={handleDuplicate}
        />
      )}
    </div>
  )
}
