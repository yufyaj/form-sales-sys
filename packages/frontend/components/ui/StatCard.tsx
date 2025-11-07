import type { ReactNode } from 'react'
import { clsx } from 'clsx'

interface StatCardProps {
  title: string
  value: string | number
  description?: string
  icon?: ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  colorClass?: string
}

/**
 * 統計情報を表示するカードコンポーネント
 * ダッシュボードの統計表示に使用
 */
export default function StatCard({
  title,
  value,
  description,
  icon,
  trend,
  colorClass = 'text-blue-600',
}: StatCardProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md">
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className={clsx('mt-2 text-3xl font-bold', colorClass)}>{value}</p>
            {description && (
              <p className="mt-1 text-sm text-gray-500">{description}</p>
            )}
          </div>
          {icon && (
            <div className={clsx('flex-shrink-0 text-4xl', colorClass)}>
              {icon}
            </div>
          )}
        </div>
        {trend && (
          <div className="mt-4 flex items-center text-sm">
            <span
              className={clsx(
                'font-medium',
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              )}
            >
              {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
            </span>
            <span className="ml-2 text-gray-500">前月比</span>
          </div>
        )}
      </div>
    </div>
  )
}
