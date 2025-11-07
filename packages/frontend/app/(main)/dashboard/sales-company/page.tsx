import type { Metadata } from 'next'
import SalesCompanyDashboard from '@/components/features/dashboard/SalesCompanyDashboard'

export const metadata: Metadata = {
  title: '営業支援会社ダッシュボード | フォーム営業支援システム',
  description: 'プロジェクト一覧と統計情報',
}

/**
 * 営業支援会社用ダッシュボードページ
 * プロジェクト一覧を表示
 */
export default function SalesCompanyDashboardPage() {
  return <SalesCompanyDashboard />
}
