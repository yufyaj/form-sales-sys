/**
 * 作業記録関連の型定義
 * バックエンドAPIスキーマに準拠
 */

/**
 * 作業記録ステータス
 */
export enum WorkRecordStatus {
  /** 送信済み */
  SENT = 'sent',
  /** 送信不可 */
  CANNOT_SEND = 'cannot_send',
}

/**
 * 作業記録ステータスラベル
 */
export const WORK_RECORD_STATUS_LABELS: Record<WorkRecordStatus, string> = {
  [WorkRecordStatus.SENT]: '送信済み',
  [WorkRecordStatus.CANNOT_SEND]: '送信不可',
}

/**
 * 送信不可理由
 */
export interface CannotSendReason {
  id: number
  reason_code: string
  reason_name: string
  description?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * 送信不可理由マスターデータ（よく使われる理由）
 */
export const COMMON_CANNOT_SEND_REASONS = [
  { code: 'FORM_NOT_FOUND', name: 'フォームが見つからない' },
  { code: 'CAPTCHA_REQUIRED', name: 'CAPTCHA認証が必要' },
  { code: 'INVALID_URL', name: '無効なURL' },
  { code: 'SITE_ERROR', name: 'サイトエラー' },
  { code: 'SUBMISSION_FAILED', name: '送信処理失敗' },
  { code: 'OTHER', name: 'その他' },
] as const

/**
 * 作業記録
 */
export interface WorkRecord {
  id: number
  assignment_id: number
  worker_id: number
  status: WorkRecordStatus
  started_at: string
  completed_at: string
  form_submission_result?: Record<string, unknown> | null
  cannot_send_reason_id?: number | null
  cannot_send_reason?: CannotSendReason | null
  notes?: string | null
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * 作業記録作成リクエスト（送信済み）
 */
export interface CreateSentWorkRecordRequest {
  assignment_id: number
  started_at: string
  completed_at: string
  form_submission_result?: Record<string, unknown>
  notes?: string
}

/**
 * 作業記録作成リクエスト（送信不可）
 */
export interface CreateCannotSendWorkRecordRequest {
  assignment_id: number
  started_at: string
  completed_at: string
  cannot_send_reason_id: number
  notes?: string
}

/**
 * 作業記録更新リクエスト
 */
export interface UpdateWorkRecordRequest {
  notes?: string
}

/**
 * 禁止時間帯チェック結果
 */
export interface ProhibitedTimeCheckResult {
  /** 現在禁止時間帯かどうか */
  isProhibited: boolean
  /** 禁止理由（複数の設定に該当する場合は配列） */
  reasons: string[]
  /** 次回許可時刻（禁止時間帯の場合） */
  nextAllowedTime?: Date
}
