'use client'

import { use } from 'react'
import { useRouter } from 'next/navigation'
import ListForm from '@/components/features/list/ListForm'
import { ListFormData } from '@/lib/validations/list'
import Card from '@/components/ui/Card'
import { createListAction } from '@/lib/actions/lists'

interface NewListPageProps {
  params: Promise<{
    id: string
  }>
}

/**
 * リスト新規作成ページ
 */
export default function NewListPage({ params }: NewListPageProps) {
  const router = useRouter()
  const { id } = use(params)
  const projectId = parseInt(id, 10)

  /**
   * リスト作成処理
   */
  const handleSubmit = async (data: ListFormData) => {
    const result = await createListAction(projectId, {
      name: data.name,
      description: data.description || null,
    })

    if (!result.success) {
      throw new Error(result.error || 'リストの作成に失敗しました')
    }

    // 成功時は一覧ページにリダイレクト
    router.push(`/projects/${projectId}/lists`)
    router.refresh()
  }

  return (
    <div className="container mx-auto max-w-2xl py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">新規リスト作成</h1>
        <p className="text-muted-foreground">
          新しいリストの情報を入力してください
        </p>
      </div>

      <Card>
        <ListForm
          projectId={projectId}
          onSubmit={handleSubmit}
          isEditMode={false}
        />
      </Card>
    </div>
  )
}
