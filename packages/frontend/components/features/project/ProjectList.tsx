'use client'

import { useRouter } from 'next/navigation'
import Table, { Column } from '@/components/ui/Table'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'

export interface Project {
  id: number
  name: string
  client_organization_id: number
  status: 'planning' | 'active' | 'completed' | 'cancelled'
  start_date: string | null
  end_date: string | null
  created_at: string
}

export interface ProjectListProps {
  projects: Project[]
  isLoading?: boolean
  onCreateClick?: () => void
}

/**
 * ステータスの日本語表示と色を取得
 */
const getStatusInfo = (
  status: Project['status']
): { label: string; variant: 'success' | 'warning' | 'default' | 'info' } => {
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
 * プロジェクト一覧コンポーネント
 */
export default function ProjectList({
  projects,
  isLoading = false,
  onCreateClick,
}: ProjectListProps) {
  const router = useRouter()

  /**
   * 日付のフォーマット
   */
  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  }

  /**
   * 行クリック時の処理
   */
  const handleRowClick = (project: Project) => {
    router.push(`/projects/${project.id}`)
  }

  /**
   * テーブルのカラム定義
   */
  const columns: Column<Project>[] = [
    {
      key: 'name',
      header: 'プロジェクト名',
      align: 'left',
    },
    {
      key: 'client_organization_id',
      header: '顧客企業ID',
      align: 'left',
      render: (project: Project) => `ID: ${project.client_organization_id}`,
    },
    {
      key: 'status',
      header: 'ステータス',
      align: 'center',
      render: (project: Project) => {
        const { label, variant } = getStatusInfo(project.status)
        return <Badge variant={variant}>{label}</Badge>
      },
    },
    {
      key: 'start_date',
      header: '開始日',
      align: 'center',
      render: (project: Project) => formatDate(project.start_date),
    },
    {
      key: 'end_date',
      header: '終了日',
      align: 'center',
      render: (project: Project) => formatDate(project.end_date),
    },
    {
      key: 'created_at',
      header: '作成日',
      align: 'center',
      render: (project: Project) => formatDate(project.created_at),
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
          <p className="mt-4 text-sm text-muted-foreground">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">プロジェクト一覧</h2>
          <p className="text-sm text-muted-foreground">
            全{projects.length}件のプロジェクト
          </p>
        </div>
        {onCreateClick && (
          <Button onClick={onCreateClick}>新規プロジェクト作成</Button>
        )}
      </div>

      {/* テーブル */}
      <Table
        columns={columns}
        data={projects}
        keyExtractor={(project) => project.id.toString()}
        onRowClick={handleRowClick}
        emptyMessage="プロジェクトがありません。新規作成してください。"
      />
    </div>
  )
}
