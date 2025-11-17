'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import ProjectForm from '@/components/features/project/ProjectForm'
import { ProjectFormData } from '@/lib/validations/project'
import Card from '@/components/ui/Card'
import { listClientOrganizations } from '@/lib/api/client-organizations'
import { createProject } from '@/lib/api/projects'

/**
 * プロジェクト新規作成ページ
 */
export default function NewProjectPage() {
  const router = useRouter()
  const [clientOrganizations, setClientOrganizations] = useState<
    Array<{ value: number; label: string }>
  >([])
  const [isLoading, setIsLoading] = useState(true)

  // 顧客企業一覧を取得
  useEffect(() => {
    const fetchClientOrganizations = async () => {
      try {
        const response = await listClientOrganizations()
        const options = response.items.map((org) => ({
          value: org.id,
          label: org.name,
        }))
        setClientOrganizations(options)
      } catch (error) {
        console.error('Failed to fetch client organizations:', error)
        // エラー時は空の配列を使用
        setClientOrganizations([])
      } finally {
        setIsLoading(false)
      }
    }

    fetchClientOrganizations()
  }, [])

  /**
   * プロジェクト作成処理
   */
  const handleSubmit = async (data: ProjectFormData) => {
    await createProject({
      name: data.name,
      client_organization_id: data.client_organization_id,
      status: data.status,
      start_date: data.start_date || null,
      end_date: data.end_date || null,
      description: data.description || null,
    })

    // 成功時は一覧ページにリダイレクト
    router.push('/projects')
    router.refresh()
  }

  if (isLoading) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">新規プロジェクト作成</h1>
          <p className="text-muted-foreground">
            新しいプロジェクトの情報を入力してください
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

  return (
    <div className="container mx-auto max-w-2xl py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">新規プロジェクト作成</h1>
        <p className="text-muted-foreground">
          新しいプロジェクトの情報を入力してください
        </p>
      </div>

      <Card>
        <ProjectForm
          clientOrganizations={clientOrganizations}
          onSubmit={handleSubmit}
          isEditMode={false}
        />
      </Card>
    </div>
  )
}
