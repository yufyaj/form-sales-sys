'use client'

import { use, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ListTable from '@/components/features/list/ListTable'
import Button from '@/components/ui/Button'
import { List } from '@/lib/api/lists'
import { getListsByProject, deleteListAction } from '@/lib/actions/lists'

interface ListsPageProps {
  params: Promise<{
    id: string
  }>
}

/**
 * リスト一覧ページ
 * プロジェクトに紐づくリストの一覧を表示
 */
export default function ListsPage({ params }: ListsPageProps) {
  const router = useRouter()
  const { id } = use(params)
  const projectId = parseInt(id, 10)

  const [lists, setLists] = useState<List[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')

  /**
   * リスト一覧を取得
   */
  useEffect(() => {
    const fetchLists = async () => {
      setIsLoading(true)
      setError('')

      try {
        const result = await getListsByProject(projectId)

        if (result.success && result.data) {
          setLists(result.data.lists)
        } else {
          setError(result.error || 'リストの取得に失敗しました')
        }
      } catch (err) {
        setError('リストの取得中にエラーが発生しました')
      } finally {
        setIsLoading(false)
      }
    }

    fetchLists()
  }, [projectId])

  /**
   * 新規作成ボタンクリック時の処理
   */
  const handleCreateClick = () => {
    router.push(`/projects/${projectId}/lists/new`)
  }

  /**
   * 削除ボタンクリック時の処理
   */
  const handleDeleteClick = async (listId: number) => {
    const result = await deleteListAction(projectId, listId)

    if (result.success) {
      // 削除成功時、リストを再取得
      const updatedResult = await getListsByProject(projectId)
      if (updatedResult.success && updatedResult.data) {
        setLists(updatedResult.data.lists)
      }
    } else {
      alert(result.error || 'リストの削除に失敗しました')
    }
  }

  /**
   * プロジェクト詳細に戻るボタン
   */
  const handleBackClick = () => {
    router.push(`/projects/${projectId}`)
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <Button variant="outline" onClick={handleBackClick} className="mb-4">
          ← プロジェクト詳細に戻る
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">リスト管理</h1>
            <p className="text-muted-foreground">
              営業先リストの作成・管理を行います
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-red-50 p-4 text-sm text-red-800" role="alert">
          {error}
        </div>
      )}

      <ListTable
        projectId={projectId}
        lists={lists}
        isLoading={isLoading}
        onCreateClick={handleCreateClick}
        onDeleteClick={handleDeleteClick}
      />
    </div>
  )
}
