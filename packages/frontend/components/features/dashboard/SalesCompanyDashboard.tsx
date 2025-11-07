'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import StatCard from '@/components/ui/StatCard'
import Table from '@/components/ui/Table'
import Badge from '@/components/ui/Badge'
import type { Project } from '@/types/project'

/**
 * プロジェクトステータスに応じたバッジのバリアント
 */
function getStatusBadgeVariant(status: Project['status']): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'planning':
      return 'default'
    case 'active':
      return 'info'
    case 'paused':
      return 'warning'
    case 'completed':
      return 'success'
    case 'archived':
      return 'default'
    default:
      return 'default'
  }
}

/**
 * プロジェクトステータスの日本語表示
 */
function getStatusLabel(status: Project['status']): string {
  switch (status) {
    case 'planning':
      return '計画中'
    case 'active':
      return '進行中'
    case 'paused':
      return '一時停止'
    case 'completed':
      return '完了'
    case 'archived':
      return 'アーカイブ'
    default:
      return status
  }
}

/**
 * 営業支援会社用ダッシュボードコンポーネント
 * プロジェクト一覧と統計情報を表示
 */
export default function SalesCompanyDashboard() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // TODO: バックエンドAPIからデータを取得する実装に置き換え
  useEffect(() => {
    // モックデータ
    const mockProjects: Project[] = [
      {
        id: '1',
        name: 'A社フォーム営業プロジェクト',
        description: '新規顧客獲得のためのフォーム営業',
        customerId: 'c1',
        customerName: 'A株式会社',
        status: 'active',
        progress: 65,
        totalLists: 5,
        completedLists: 3,
        totalSubmissions: 1250,
        createdAt: '2025-01-15T09:00:00Z',
        updatedAt: '2025-02-01T14:30:00Z',
      },
      {
        id: '2',
        name: 'B社リード獲得キャンペーン',
        description: '春季キャンペーン向けリード獲得',
        customerId: 'c2',
        customerName: 'B株式会社',
        status: 'active',
        progress: 40,
        totalLists: 3,
        completedLists: 1,
        totalSubmissions: 680,
        createdAt: '2025-02-01T10:00:00Z',
        updatedAt: '2025-02-05T16:45:00Z',
      },
      {
        id: '3',
        name: 'C社市場調査プロジェクト',
        description: '新製品の市場調査',
        customerId: 'c3',
        customerName: 'C株式会社',
        status: 'completed',
        progress: 100,
        totalLists: 2,
        completedLists: 2,
        totalSubmissions: 450,
        createdAt: '2025-01-10T08:00:00Z',
        updatedAt: '2025-01-31T18:00:00Z',
      },
    ]

    setProjects(mockProjects)
    setIsLoading(false)
  }, [])

  // 統計情報の計算
  const stats = {
    totalProjects: projects.length,
    activeProjects: projects.filter(p => p.status === 'active').length,
    completedProjects: projects.filter(p => p.status === 'completed').length,
    totalSubmissions: projects.reduce((sum, p) => sum + p.totalSubmissions, 0),
  }

  // テーブル列定義
  const columns = [
    {
      key: 'name',
      header: 'プロジェクト名',
      render: (project: Project) => (
        <div>
          <div className="text-sm font-medium text-gray-900">{project.name}</div>
          <div className="text-sm text-gray-500">{project.customerName}</div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'ステータス',
      render: (project: Project) => (
        <Badge variant={getStatusBadgeVariant(project.status)}>
          {getStatusLabel(project.status)}
        </Badge>
      ),
    },
    {
      key: 'progress',
      header: '進捗',
      render: (project: Project) => (
        <div className="flex items-center">
          <div className="h-2 w-32 overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full bg-blue-600 transition-all"
              style={{ width: `${project.progress}%` }}
            />
          </div>
          <span className="ml-2 text-sm text-gray-600">{project.progress}%</span>
        </div>
      ),
    },
    {
      key: 'totalLists',
      header: 'リスト数',
      render: (project: Project) => (
        <div className="text-sm text-gray-900">
          {project.completedLists} / {project.totalLists}
        </div>
      ),
    },
    {
      key: 'totalSubmissions',
      header: '送信数',
      render: (project: Project) => (
        <div className="text-sm font-medium text-gray-900">
          {project.totalSubmissions.toLocaleString()}
        </div>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-4 sm:p-6 lg:p-8">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
            プロジェクト一覧
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            進行中のプロジェクトと統計情報
          </p>
        </div>
        <button
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          onClick={() => {
            // TODO: プロジェクト作成ページへ遷移
            console.log('プロジェクト作成')
          }}
        >
          新規プロジェクト
        </button>
      </div>

      {/* 統計カード */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="総プロジェクト数"
          value={stats.totalProjects}
          description="全プロジェクト"
          colorClass="text-blue-600"
        />
        <StatCard
          title="進行中"
          value={stats.activeProjects}
          description="アクティブなプロジェクト"
          colorClass="text-green-600"
        />
        <StatCard
          title="完了"
          value={stats.completedProjects}
          description="完了したプロジェクト"
          colorClass="text-purple-600"
        />
        <StatCard
          title="総送信数"
          value={stats.totalSubmissions.toLocaleString()}
          description="全プロジェクト合計"
          colorClass="text-orange-600"
        />
      </div>

      {/* プロジェクト一覧テーブル */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          プロジェクト
        </h2>
        <Table
          columns={columns}
          data={projects}
          keyExtractor={(project) => project.id}
          onRowClick={(project) => {
            // TODO: プロジェクト詳細ページへ遷移
            router.push(`/dashboard/sales-company/projects/${project.id}`)
          }}
          emptyMessage="プロジェクトがありません"
        />
      </div>
    </div>
  )
}
