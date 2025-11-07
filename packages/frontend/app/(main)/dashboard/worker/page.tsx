import type { Metadata } from 'next'
import WorkerDashboard from '@/components/features/dashboard/WorkerDashboard'

export const metadata: Metadata = {
  title: 'ワーカーダッシュボード | フォーム営業支援システム',
  description: '割り当てリスト一覧とタスク状況',
}

/**
 * ワーカー用ダッシュボードページ
 * 割り当てリスト一覧を表示
 */
export default function WorkerDashboardPage() {
  return <WorkerDashboard />
}
