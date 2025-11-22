'use client'

import { use, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import WorkerAssignmentForm from '@/components/features/list/WorkerAssignmentForm'
import type { AssignmentFormData } from '@/lib/validations/assignment'
import { listWorkers } from '@/lib/api/users'
import { createAssignment } from '@/lib/api/assignments'
import type { User } from '@/types/user'
import Card from '@/components/ui/Card'

interface AssignWorkersPageProps {
  params: Promise<{
    id: string
    listId: string
  }>
}

/**
 * ワーカー割り当てページ
 */
export default function AssignWorkersPage({ params }: AssignWorkersPageProps) {
  const router = useRouter()
  const { id, listId } = use(params)
  const projectId = parseInt(id, 10)
  const listIdNum = parseInt(listId, 10)

  // パラメータのバリデーション
  if (isNaN(projectId) || isNaN(listIdNum)) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-800">
          無効なプロジェクトIDまたはリストIDです
        </div>
      </div>
    )
  }

  const [workers, setWorkers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')

  /**
   * ワーカー一覧を取得
   */
  useEffect(() => {
    const fetchWorkers = async () => {
      try {
        setIsLoading(true)
        setError('')
        const response = await listWorkers()
        setWorkers(response.users)
      } catch (err) {
        setError('ワーカー一覧の取得に失敗しました')
        // 開発環境のみ詳細ログを出力
        if (process.env.NODE_ENV === 'development') {
          console.error('Failed to fetch workers:', err)
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchWorkers()
  }, [])

  /**
   * ワーカー割り当て処理
   */
  const handleSubmit = async (data: AssignmentFormData) => {
    await createAssignment(projectId, listIdNum, {
      worker_id: data.workerId,
      start_row: data.startRow,
      end_row: data.endRow,
      priority: data.priority,
      due_date: data.dueDate || null,
    })

    // 成功時は前の画面に戻る
    router.back()
    router.refresh()
  }

  /**
   * ローディング中
   */
  if (isLoading) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="text-center">
          <p className="text-muted-foreground">読み込み中...</p>
        </div>
      </div>
    )
  }

  /**
   * エラー表示
   */
  if (error) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      </div>
    )
  }

  /**
   * ワーカーが0件
   */
  if (workers.length === 0) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="rounded-md bg-yellow-50 p-4 text-sm text-yellow-800">
          アクティブなワーカーが登録されていません
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-2xl py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">ワーカー割り当て</h1>
        <p className="text-muted-foreground">
          リストにワーカーを割り当てて作業を開始します
        </p>
      </div>

      <Card>
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listIdNum}
          workers={workers}
          onSubmit={handleSubmit}
        />
      </Card>
    </div>
  )
}
