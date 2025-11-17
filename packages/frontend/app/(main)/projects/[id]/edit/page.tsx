'use client'

import { useRouter } from 'next/navigation'
import { notFound } from 'next/navigation'
import ProjectForm from '@/components/features/project/ProjectForm'
import { ProjectFormData } from '@/lib/validations/project'
import Card from '@/components/ui/Card'

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

  if (isNaN(projectId)) {
    notFound()
  }

  // TODO: バックエンドAPIから既存プロジェクト情報を取得
  // const project = await fetchProject(projectId)

  // 仮のデータ
  const project = {
    name: 'サンプルプロジェクト',
    client_organization_id: 1,
    status: 'active' as const,
    start_date: '2025-04-01',
    end_date: '2025-09-30',
    description: 'これはサンプルプロジェクトの説明です。',
  }

  // TODO: バックエンドAPIから顧客企業一覧を取得
  const clientOrganizations = [
    { value: 1, label: '株式会社サンプルA' },
    { value: 2, label: '株式会社サンプルB' },
    { value: 3, label: '株式会社サンプルC' },
  ]

  /**
   * プロジェクト更新処理
   */
  const handleSubmit = async (data: ProjectFormData) => {
    // TODO: バックエンドAPIにPATCHリクエストを送信
    console.log('プロジェクト更新:', data)

    // 仮の処理
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // 成功時は詳細ページにリダイレクト
    router.push(`/projects/${projectId}`)
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
