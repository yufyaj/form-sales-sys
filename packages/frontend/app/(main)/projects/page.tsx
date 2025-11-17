import { Suspense } from 'react'
import Link from 'next/link'
import ProjectList from '@/components/features/project/ProjectList'
import Button from '@/components/ui/Button'

/**
 * プロジェクト一覧ページ
 * 営業支援会社に属するプロジェクトの一覧を表示
 */
export default async function ProjectsPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">プロジェクト管理</h1>
          <p className="text-muted-foreground">
            営業プロジェクトの作成・管理を行います
          </p>
        </div>
        <Link href="/projects/new">
          <Button>新規プロジェクト作成</Button>
        </Link>
      </div>

      <Suspense fallback={<ProjectListSkeleton />}>
        <ProjectListWrapper />
      </Suspense>
    </div>
  )
}

/**
 * プロジェクト一覧データ取得コンポーネント
 */
async function ProjectListWrapper() {
  // TODO: バックエンドAPIからプロジェクト一覧を取得
  // const projects = await fetchProjects()

  // 仮のデータ（後でAPIから取得するように変更）
  const projects = []

  return <ProjectList projects={projects} />
}

/**
 * ローディング用スケルトン
 */
function ProjectListSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-12 w-full animate-pulse rounded-md bg-muted" />
      <div className="h-64 w-full animate-pulse rounded-md bg-muted" />
    </div>
  )
}
