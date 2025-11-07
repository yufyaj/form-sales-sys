'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import StatCard from '@/components/ui/StatCard'
import Table from '@/components/ui/Table'
import Badge from '@/components/ui/Badge'
import type { Assignment } from '@/types/assignment'

/**
 * 割り当てステータスに応じたバッジのバリアント
 */
function getStatusBadgeVariant(status: Assignment['status']): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'assigned':
      return 'default'
    case 'in_progress':
      return 'info'
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    default:
      return 'default'
  }
}

/**
 * 割り当てステータスの日本語表示
 */
function getStatusLabel(status: Assignment['status']): string {
  switch (status) {
    case 'assigned':
      return '割り当て済み'
    case 'in_progress':
      return '作業中'
    case 'completed':
      return '完了'
    case 'failed':
      return '失敗'
    default:
      return status
  }
}

/**
 * 優先度に応じたバッジのバリアント
 */
function getPriorityBadgeVariant(priority: Assignment['priority']): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  switch (priority) {
    case 'low':
      return 'default'
    case 'medium':
      return 'info'
    case 'high':
      return 'warning'
    case 'urgent':
      return 'danger'
    default:
      return 'default'
  }
}

/**
 * 優先度の日本語表示
 */
function getPriorityLabel(priority: Assignment['priority']): string {
  switch (priority) {
    case 'low':
      return '低'
    case 'medium':
      return '中'
    case 'high':
      return '高'
    case 'urgent':
      return '緊急'
    default:
      return priority
  }
}

/**
 * ワーカー用ダッシュボードコンポーネント
 * 割り当てリスト一覧とタスク状況を表示
 */
export default function WorkerDashboard() {
  const { user } = useAuth()
  const router = useRouter()
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // TODO: バックエンドAPIからデータを取得する実装に置き換え
  useEffect(() => {
    if (!user) return

    // モックデータ（現在のユーザーに割り当てられたタスク）
    const mockAssignments: Assignment[] = [
      {
        id: '1',
        listId: 'l1',
        listName: 'IT企業リスト（東京）',
        projectId: 'p1',
        projectName: 'A社フォーム営業プロジェクト',
        workerId: user.id,
        status: 'in_progress',
        priority: 'high',
        recordsToProcess: 500,
        processedRecords: 325,
        successCount: 300,
        failureCount: 25,
        assignedAt: '2025-02-01T09:00:00Z',
        startedAt: '2025-02-01T10:00:00Z',
        dueDate: '2025-02-10T18:00:00Z',
      },
      {
        id: '2',
        listId: 'l2',
        listName: '製造業リスト（大阪）',
        projectId: 'p1',
        projectName: 'A社フォーム営業プロジェクト',
        workerId: user.id,
        status: 'assigned',
        priority: 'medium',
        recordsToProcess: 300,
        processedRecords: 0,
        successCount: 0,
        failureCount: 0,
        assignedAt: '2025-02-05T14:00:00Z',
        dueDate: '2025-02-15T18:00:00Z',
      },
      {
        id: '3',
        listId: 'l3',
        listName: '小売業リスト（全国）',
        projectId: 'p2',
        projectName: 'B社リード獲得キャンペーン',
        workerId: user.id,
        status: 'completed',
        priority: 'low',
        recordsToProcess: 200,
        processedRecords: 200,
        successCount: 185,
        failureCount: 15,
        assignedAt: '2025-01-25T09:00:00Z',
        startedAt: '2025-01-25T10:00:00Z',
        completedAt: '2025-01-30T16:30:00Z',
        dueDate: '2025-02-05T18:00:00Z',
      },
      {
        id: '4',
        listId: 'l4',
        listName: '金融機関リスト（東京・大阪）',
        projectId: 'p1',
        projectName: 'A社フォーム営業プロジェクト',
        workerId: user.id,
        status: 'assigned',
        priority: 'urgent',
        recordsToProcess: 150,
        processedRecords: 0,
        successCount: 0,
        failureCount: 0,
        assignedAt: '2025-02-06T09:00:00Z',
        dueDate: '2025-02-08T18:00:00Z',
      },
    ]

    setAssignments(mockAssignments)
    setIsLoading(false)
  }, [user])

  // 統計情報の計算
  const stats = {
    totalAssignments: assignments.length,
    inProgress: assignments.filter(a => a.status === 'in_progress').length,
    pending: assignments.filter(a => a.status === 'assigned').length,
    completed: assignments.filter(a => a.status === 'completed').length,
    totalRecordsToProcess: assignments
      .filter(a => a.status !== 'completed')
      .reduce((sum, a) => sum + a.recordsToProcess, 0),
    totalProcessedRecords: assignments.reduce((sum, a) => sum + a.processedRecords, 0),
  }

  // テーブル列定義
  const columns = [
    {
      key: 'priority',
      header: '優先度',
      render: (assignment: Assignment) => (
        <Badge variant={getPriorityBadgeVariant(assignment.priority)} size="sm">
          {getPriorityLabel(assignment.priority)}
        </Badge>
      ),
    },
    {
      key: 'listName',
      header: 'リスト名',
      render: (assignment: Assignment) => (
        <div>
          <div className="text-sm font-medium text-gray-900">{assignment.listName}</div>
          <div className="text-sm text-gray-500">{assignment.projectName}</div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'ステータス',
      render: (assignment: Assignment) => (
        <Badge variant={getStatusBadgeVariant(assignment.status)}>
          {getStatusLabel(assignment.status)}
        </Badge>
      ),
    },
    {
      key: 'progress',
      header: '進捗',
      render: (assignment: Assignment) => {
        const progress = assignment.recordsToProcess > 0
          ? Math.round((assignment.processedRecords / assignment.recordsToProcess) * 100)
          : 0
        return (
          <div className="flex items-center">
            <div className="h-2 w-32 overflow-hidden rounded-full bg-gray-200">
              <div
                className="h-full bg-blue-600 transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="ml-2 text-sm text-gray-600">{progress}%</span>
          </div>
        )
      },
    },
    {
      key: 'records',
      header: '処理状況',
      render: (assignment: Assignment) => (
        <div className="text-sm text-gray-900">
          {assignment.processedRecords} / {assignment.recordsToProcess}
        </div>
      ),
    },
    {
      key: 'dueDate',
      header: '期限',
      render: (assignment: Assignment) => {
        if (!assignment.dueDate) return <span className="text-sm text-gray-400">-</span>
        const dueDate = new Date(assignment.dueDate)
        const now = new Date()
        const isOverdue = dueDate < now && assignment.status !== 'completed'
        return (
          <div className={`text-sm ${isOverdue ? 'font-medium text-red-600' : 'text-gray-500'}`}>
            {dueDate.toLocaleDateString('ja-JP')}
          </div>
        )
      },
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
          割り当てリスト一覧
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          あなたに割り当てられたタスクの状況
        </p>
      </div>

      {/* 統計カード */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="割り当て中"
          value={stats.pending}
          description="未着手のタスク"
          colorClass="text-gray-600"
        />
        <StatCard
          title="作業中"
          value={stats.inProgress}
          description="現在進行中"
          colorClass="text-blue-600"
        />
        <StatCard
          title="完了"
          value={stats.completed}
          description="完了したタスク"
          colorClass="text-green-600"
        />
        <StatCard
          title="処理進捗"
          value={`${stats.totalProcessedRecords} / ${stats.totalProcessedRecords + stats.totalRecordsToProcess}`}
          description="総処理レコード数"
          colorClass="text-purple-600"
        />
      </div>

      {/* 割り当て一覧テーブル */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          タスク一覧
        </h2>
        <Table<Assignment>
          columns={columns}
          data={assignments}
          keyExtractor={(assignment) => assignment.id}
          onRowClick={(assignment) => {
            // TODO: タスク詳細ページへ遷移
            router.push(`/dashboard/worker/assignments/${assignment.id}`)
          }}
          emptyMessage="割り当てられたタスクがありません"
        />
      </div>
    </div>
  )
}
