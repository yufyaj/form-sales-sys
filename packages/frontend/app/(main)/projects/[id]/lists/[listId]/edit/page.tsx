'use client'

import { use, useEffect, useState } from 'react'
import { useRouter, notFound } from 'next/navigation'
import ListForm from '@/components/features/list/ListForm'
import { ListFormData } from '@/lib/validations/list'
import Card from '@/components/ui/Card'
import { getListDetail, updateListAction } from '@/lib/actions/lists'

interface EditListPageProps {
  params: Promise<{
    id: string
    listId: string
  }>
}

/**
 * リスト編集ページ
 */
export default function EditListPage({ params }: EditListPageProps) {
  const router = useRouter()
  const { id, listId } = use(params)
  const projectId = parseInt(id, 10)
  const listIdNum = parseInt(listId, 10)

  const [list, setList] = useState<ListFormData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  if (isNaN(projectId) || isNaN(listIdNum)) {
    notFound()
  }

  // リスト情報を取得
  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getListDetail(projectId, listIdNum)

        if (result.success && result.data) {
          setList({
            name: result.data.name,
            description: result.data.description || undefined,
          })
        } else {
          setError(result.error || 'リスト情報の取得に失敗しました')
        }
      } catch (err) {
        console.error('Failed to fetch list:', err)
        setError('データの取得に失敗しました')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [projectId, listIdNum])

  /**
   * リスト更新処理
   */
  const handleSubmit = async (data: ListFormData) => {
    const result = await updateListAction(projectId, listIdNum, {
      name: data.name,
      description: data.description || null,
    })

    if (!result.success) {
      throw new Error(result.error || 'リストの更新に失敗しました')
    }

    // 成功時は一覧ページにリダイレクト
    router.push(`/projects/${projectId}/lists`)
    router.refresh()
  }

  if (isLoading) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">リスト編集</h1>
          <p className="text-muted-foreground">
            リストの情報を変更します
          </p>
        </div>
        <Card>
          <div className="flex h-64 items-center justify-center">
            <div className="text-muted-foreground">読み込み中...</div>
          </div>
        </Card>
      </div>
    )
  }

  if (error || !list) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">リスト編集</h1>
          <p className="text-muted-foreground">
            リストの情報を変更します
          </p>
        </div>
        <Card>
          <div className="flex h-64 items-center justify-center">
            <div className="text-destructive">
              {error || 'リストが見つかりません'}
            </div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-2xl py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">リスト編集</h1>
        <p className="text-muted-foreground">
          リストの情報を変更します
        </p>
      </div>

      <Card>
        <ListForm
          projectId={projectId}
          defaultValues={list}
          onSubmit={handleSubmit}
          isEditMode={true}
        />
      </Card>
    </div>
  )
}
