import { Suspense } from 'react'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'

interface ProjectDetailPageProps {
  params: {
    id: string
  }
}

/**
 * プロジェクト詳細ページ
 */
export default async function ProjectDetailPage({
  params,
}: ProjectDetailPageProps) {
  const projectId = parseInt(params.id, 10)

  if (isNaN(projectId)) {
    notFound()
  }

  return (
    <div className="container mx-auto py-8">
      <Suspense fallback={<ProjectDetailSkeleton />}>
        <ProjectDetailWrapper projectId={projectId} />
      </Suspense>
    </div>
  )
}

/**
 * プロジェクト詳細データ取得コンポーネント
 */
async function ProjectDetailWrapper({ projectId }: { projectId: number }) {
  let project
  let clientOrganizationName = '読み込み中...'

  try {
    const { getProject } = await import('@/lib/api/projects')
    const { getClientOrganization } = await import('@/lib/api/client-organizations')

    project = await getProject(projectId)

    // 顧客組織情報を取得
    try {
      const clientOrg = await getClientOrganization(project.client_organization_id)
      clientOrganizationName = clientOrg.name
    } catch (error) {
      console.error('Failed to fetch client organization:', error)
      clientOrganizationName = `ID: ${project.client_organization_id}`
    }
  } catch (error) {
    console.error('Failed to fetch project:', error)
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-destructive">
          プロジェクトの読み込みに失敗しました
        </div>
      </div>
    )
  }

  const statusInfo = getStatusInfo(project.status)

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <div className="mb-2 flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
            <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
          </div>
          <p className="text-muted-foreground">
            顧客企業: {clientOrganizationName}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href={`/projects/${projectId}/edit`}>
            <Button variant="outline">編集</Button>
          </Link>
          <Link href="/projects">
            <Button variant="outline">一覧に戻る</Button>
          </Link>
        </div>
      </div>

      {/* プロジェクト詳細 */}
      <Card>
        <div className="space-y-6">
          <div>
            <h2 className="mb-4 text-xl font-semibold">プロジェクト情報</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-muted-foreground">開始日</dt>
                <dd className="mt-1 text-sm">
                  {project.start_date
                    ? new Date(project.start_date).toLocaleDateString('ja-JP')
                    : '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">終了日</dt>
                <dd className="mt-1 text-sm">
                  {project.end_date
                    ? new Date(project.end_date).toLocaleDateString('ja-JP')
                    : '-'}
                </dd>
              </div>
              <div className="col-span-2">
                <dt className="text-sm font-medium text-muted-foreground">説明</dt>
                <dd className="mt-1 text-sm whitespace-pre-wrap">
                  {project.description || '説明はありません'}
                </dd>
              </div>
            </dl>
          </div>

          <div className="border-t pt-4">
            <h2 className="mb-4 text-xl font-semibold">システム情報</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-muted-foreground">作成日時</dt>
                <dd className="mt-1 text-sm">
                  {new Date(project.created_at).toLocaleString('ja-JP')}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">更新日時</dt>
                <dd className="mt-1 text-sm">
                  {new Date(project.updated_at).toLocaleString('ja-JP')}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </Card>
    </div>
  )
}

/**
 * ステータスの情報を取得
 */
function getStatusInfo(status: 'planning' | 'active' | 'completed' | 'cancelled'): {
  label: string
  variant: 'success' | 'warning' | 'default' | 'info'
} {
  switch (status) {
    case 'planning':
      return { label: '企画中', variant: 'default' }
    case 'active':
      return { label: '進行中', variant: 'success' }
    case 'completed':
      return { label: '完了', variant: 'info' }
    case 'cancelled':
      return { label: 'キャンセル', variant: 'warning' }
  }
}

/**
 * ローディング用スケルトン
 */
function ProjectDetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-20 w-full animate-pulse rounded-md bg-muted" />
      <div className="h-96 w-full animate-pulse rounded-md bg-muted" />
    </div>
  )
}
