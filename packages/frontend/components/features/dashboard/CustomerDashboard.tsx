'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
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
 * 顧客用ダッシュボードコンポーネント
 * 依頼プロジェクト一覧と進捗を表示
 */
export default function CustomerDashboard() {
  const { user } = useAuth()
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // TODO: バックエンドAPIからデータを取得する実装に置き換え
  useEffect(() => {
    if (!user) return

    // モックデータ（現在のユーザーが顧客として依頼しているプロジェクト）
    const mockProjects: Project[] = [
      {
        id: '1',
        name: '新規顧客獲得キャンペーン',
        description: '春季の新規顧客獲得のためのフォーム営業',
        customerId: user.id,
        customerName: user.name || 'ユーザー',
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
        name: '製品プロモーションプロジェクト',
        description: '新製品のプロモーション向けリード獲得',
        customerId: user.id,
        customerName: user.name || 'ユーザー',
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
        name: '市場調査プロジェクト',
        description: '競合分析のための市場調査',
        customerId: user.id,
        customerName: user.name || 'ユーザー',
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
  }, [user])

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
          {project.description && (
            <div className="mt-1 text-sm text-gray-500">{project.description}</div>
          )}
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
      key: 'totalSubmissions',
      header: '送信数',
      render: (project: Project) => (
        <div className="text-sm font-medium text-gray-900">
          {project.totalSubmissions.toLocaleString()}
        </div>
      ),
    },
    {
      key: 'createdAt',
      header: '作成日',
      render: (project: Project) => (
        <div className="text-sm text-gray-500">
          {new Date(project.createdAt).toLocaleDateString('ja-JP')}
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
      <div>
        <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
          依頼プロジェクト一覧
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          あなたが依頼したプロジェクトの進捗状況
        </p>
      </div>

      {/* 統計カード */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="依頼中プロジェクト"
          value={stats.totalProjects}
          description="全プロジェクト"
          colorClass="text-blue-600"
        />
        <StatCard
          title="進行中"
          value={stats.activeProjects}
          description="現在進行中"
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
        <Table<Project>
          columns={columns}
          data={projects}
          keyExtractor={(project) => project.id}
          onRowClick={(project) => {
            // TODO: プロジェクト詳細ページへ遷移
            router.push(`/dashboard/customer/projects/${project.id}`)
          }}
          emptyMessage="依頼中のプロジェクトがありません"
        />
      </div>
    </div>
  )
}
