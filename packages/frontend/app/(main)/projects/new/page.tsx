'use client'

import { useRouter } from 'next/navigation'
import ProjectForm from '@/components/features/project/ProjectForm'
import { ProjectFormData } from '@/lib/validations/project'
import Card from '@/components/ui/Card'

/**
 * プロジェクト新規作成ページ
 */
export default function NewProjectPage() {
  const router = useRouter()

  // TODO: バックエンドAPIから顧客企業一覧を取得
  // const clientOrganizations = await fetchClientOrganizations()

  // 仮のデータ（後でAPIから取得するように変更）
  const clientOrganizations = [
    { value: 1, label: '株式会社サンプルA' },
    { value: 2, label: '株式会社サンプルB' },
    { value: 3, label: '株式会社サンプルC' },
  ]

  /**
   * プロジェクト作成処理
   */
  const handleSubmit = async (data: ProjectFormData) => {
    // TODO: バックエンドAPIにPOSTリクエストを送信
    console.log('プロジェクト作成:', data)

    // 仮の処理（後でAPIコールに置き換え）
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // 成功時は一覧ページにリダイレクト
    router.push('/projects')
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
