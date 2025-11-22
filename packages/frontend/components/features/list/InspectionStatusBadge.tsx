import Badge from '@/components/ui/Badge'
import { InspectionStatus } from '@/types/list'

interface InspectionStatusBadgeProps {
  status: InspectionStatus
  size?: 'sm' | 'md' | 'lg'
}

/**
 * 検収ステータスバッジコンポーネント
 * 検収状態を視覚的に表示するためのバッジ
 */
export default function InspectionStatusBadge({
  status,
  size = 'md',
}: InspectionStatusBadgeProps) {
  /**
   * ステータスに応じたバリアントとテキストを決定
   */
  const getStatusConfig = (status: InspectionStatus) => {
    switch (status) {
      case 'not_started':
        return {
          variant: 'default' as const,
          label: '未検収',
        }
      case 'in_progress':
        return {
          variant: 'info' as const,
          label: '検収中',
        }
      case 'completed':
        return {
          variant: 'success' as const,
          label: '検収完了',
        }
      case 'rejected':
        return {
          variant: 'danger' as const,
          label: '却下',
        }
    }
  }

  const config = getStatusConfig(status)

  return (
    <Badge
      variant={config.variant}
      size={size}
      role="status"
      aria-label={`検収ステータス: ${config.label}`}
    >
      {config.label}
    </Badge>
  )
}
