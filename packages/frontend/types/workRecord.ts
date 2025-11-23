/**
 * 作業記録関連の型定義
 */

/**
 * 作業ステータス
 */
export type WorkRecordStatus = 'sent' | 'cannot_send'

/**
 * フォーム送信結果
 */
export interface FormSubmissionResult {
  statusCode?: number
  message?: string
  responseTimeMs?: number
  screenshotUrl?: string
  errorMessage?: string
  retryCount?: number
}

/**
 * 作業記録
 */
export interface WorkRecord {
  id: number
  assignmentId: number // リスト項目割り当てID
  workerId: number
  status: WorkRecordStatus
  startedAt: string
  completedAt?: string
  formSubmissionResult?: FormSubmissionResult
  cannotSendReasonId?: number
  notes?: string
  createdAt: string
  updatedAt: string
}

/**
 * 作業記録作成リクエスト
 */
export interface WorkRecordCreateRequest {
  assignmentId: number
  workerId: number
  status: WorkRecordStatus
  startedAt: string
  completedAt?: string
  formSubmissionResult?: FormSubmissionResult
  cannotSendReasonId?: number
  notes?: string
}

/**
 * 作業記録更新リクエスト
 */
export interface WorkRecordUpdateRequest {
  status?: WorkRecordStatus
  completedAt?: string
  formSubmissionResult?: FormSubmissionResult
  cannotSendReasonId?: number
  notes?: string
}

/**
 * 作業記録一覧のレスポンス
 */
export interface WorkRecordListResponse {
  workRecords: WorkRecord[]
  total: number
  page?: number
  pageSize?: number
}

/**
 * 作業記録フォームデータ
 */
export interface WorkRecordFormData {
  status: WorkRecordStatus
  cannotSendReasonId?: number
  notes?: string
}
