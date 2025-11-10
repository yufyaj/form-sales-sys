'use client'

import type { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { fadeInUp, transitions } from '@/lib/motion'

interface StatCardProps {
  title: string
  value: string | number
  description?: string
  icon?: ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  variant?: 'default' | 'gradient' | 'outline'
}

/**
 * モダンな統計カードコンポーネント
 * ダッシュボードで使用する洗練されたデザイン
 *
 * @example
 * ```tsx
 * <StatCard
 *   title="総売上"
 *   value="¥1,234,567"
 *   description="今月の売上"
 *   icon={<TrendingUp />}
 *   trend={{ value: 12.5, isPositive: true }}
 *   variant="gradient"
 * />
 * ```
 */
export default function StatCard({
  title,
  value,
  description,
  icon,
  trend,
  variant = 'default',
}: StatCardProps) {
  const variants = {
    default: 'bg-card border hover:shadow-md',
    gradient: 'bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950 dark:to-primary-900 border-0 hover:shadow-lg',
    outline: 'bg-background border-2 hover:border-primary',
  }

  const MotionDiv = motion.div as any

  return (
    <MotionDiv
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
      whileHover="hover"
      className={cn(
        'group overflow-hidden rounded-lg shadow-sm transition-all duration-base',
        variants[variant]
      )}
    >
      <MotionDiv
        className="p-6"
        variants={{
          hover: { y: -4 },
        }}
        transition={transitions.smooth}
      >
        {/* ヘッダー部分 */}
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold tracking-tight text-foreground">
              {value}
            </p>
          </div>

          {/* アイコン */}
          {icon && (
            <div
              className={cn(
                'flex h-12 w-12 items-center justify-center rounded-lg',
                'bg-primary/10 text-primary transition-all duration-base',
                'group-hover:scale-110 group-hover:bg-primary/20'
              )}
            >
              <div className="h-6 w-6">{icon}</div>
            </div>
          )}
        </div>

        {/* 説明文 */}
        {description && (
          <p className="mt-2 text-sm text-muted-foreground">{description}</p>
        )}

        {/* トレンド表示 */}
        {trend && (
          <div className="mt-4 flex items-center gap-2">
            <div
              className={cn(
                'inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium',
                trend.isPositive
                  ? 'bg-success/10 text-success'
                  : 'bg-destructive/10 text-destructive'
              )}
            >
              <svg
                className={cn(
                  'h-3 w-3',
                  !trend.isPositive && 'rotate-180'
                )}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 10l7-7m0 0l7 7m-7-7v18"
                />
              </svg>
              <span>{Math.abs(trend.value)}%</span>
            </div>
            <span className="text-xs text-muted-foreground">前月比</span>
          </div>
        )}
      </MotionDiv>

      {/* ホバー時のボトムボーダー */}
      <MotionDiv
        className="h-1 bg-gradient-to-r from-primary-500 to-primary-600"
        variants={{
          hover: { width: '100%' },
        }}
        initial={{ width: 0 }}
        transition={transitions.ease}
      />
    </MotionDiv>
  )
}
