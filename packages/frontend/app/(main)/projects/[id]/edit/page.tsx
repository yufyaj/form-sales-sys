'use client'

import { useRouter } from 'next/navigation'
import { notFound } from 'next/navigation'
import { useEffect, useState } from 'react'
import ProjectForm from '@/components/features/project/ProjectForm'
import { ProjectFormData } from '@/lib/validations/project'
import Card from '@/components/ui/Card'
import { getProject, updateProject } from '@/lib/api/projects'
import { listClientOrganizations } from '@/lib/api/client-organizations'

interface EditProjectPageProps {
  params: {
    id: string
  }
}

/**
 * プロジェクト編集ページ
 */
export default function EditProjectPage({ params }: EditProjectPageProps) {
  const router = useRouter()
  const projectId = parseInt(params.id, 10)

  const [project, setProject] = useState<ProjectFormData | null>(null)
  const [clientOrganizations, setClientOrganizations] = useState<
    Array<{ value: number; label: string }>
  >([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  if (isNaN(projectId)) {
    notFound()
  }

  // プロジェクト情報と顧客企業一覧を取得
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectData, clientOrgsResponse] = await Promise.all([
          getProject(projectId),
          listClientOrganizations(),
        ])

        setProject({
          name: projectData.name,
          client_organization_id: projectData.client_organization_id,
          status: projectData.status,
          start_date: projectData.start_date || undefined,
          end_date: projectData.end_date || undefined,
          description: projectData.description || undefined,
        })

        const options = clientOrgsResponse.items.map((org) => ({
          value: org.id,
          label: org.name,
        }))
        setClientOrganizations(options)
      } catch (err) {
        console.error('Failed to fetch data:', err)
        setError('データの取得に失敗しました')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [projectId])

  /**
   * プロジェクト更新処理
   */
  const handleSubmit = async (data: ProjectFormData) => {
    await updateProject(projectId, {
      name: data.name,
      client_organization_id: data.client_organization_id,
      status: data.status,
      start_date: data.start_date || null,
      end_date: data.end_date || null,
      description: data.description || null,
    })

    // 成功時は詳細ページにリダイレクト
    router.push(`/projects/${projectId}`)
    router.refresh()
  }

  if (isLoading) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">プロジェクト編集</h1>
          <p className="text-muted-foreground">
            プロジェクトの情報を変更します
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

  if (error || !project) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">プロジェクト編集</h1>
          <p className="text-muted-foreground">
            プロジェクトの情報を変更します
          </p>
        </div>
        <Card>
          <div className="flex h-64 items-center justify-center">
            <div className="text-destructive">
              {error || 'プロジェクトが見つかりません'}
            </div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-2xl py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">プロジェクト編集</h1>
        <p className="text-muted-foreground">
          プロジェクトの情報を変更します
        </p>
      </div>

      <Card>
        <ProjectForm
          clientOrganizations={clientOrganizations}
          defaultValues={project}
          onSubmit={handleSubmit}
          isEditMode={true}
        />
      </Card>
    </div>
  )
}
