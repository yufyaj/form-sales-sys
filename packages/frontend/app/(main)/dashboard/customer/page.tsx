import type { Metadata } from 'next'
import CustomerDashboard from '@/components/features/dashboard/CustomerDashboard'

export const metadata: Metadata = {
  title: '顧客ダッシュボード | フォーム営業支援システム',
  description: '依頼プロジェクト一覧と進捗状況',
}

/**
 * 顧客用ダッシュボードページ
 * 依頼プロジェクト一覧を表示
 */
export default function CustomerDashboardPage() {
  return <CustomerDashboard />
}
