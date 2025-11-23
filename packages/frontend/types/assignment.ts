/**
 * 割り当て（ワーカータスク）関連の型定義
 */

/**
 * 割り当てステータス
 */
export type AssignmentStatus = 'assigned' | 'in_progress' | 'completed' | 'failed'

/**
 * 割り当て優先度
 */
export type AssignmentPriority = 'low' | 'medium' | 'high' | 'urgent'

/**
 * 割り当て
 */
export interface Assignment {
  id: string
  listId: string
  listName: string // リスト名（結合済み）
  projectId: string
  projectName: string // プロジェクト名（結合済み）
  workerId: string
  status: AssignmentStatus
  priority: AssignmentPriority
  recordsToProcess: number // 処理対象レコード数
  processedRecords: number // 処理済みレコード数
  successCount: number // 成功数
  failureCount: number // 失敗数
  assignedAt: string
  startedAt?: string
  completedAt?: string
  dueDate?: string // 期限
}

/**
 * 割り当て一覧のレスポンス
 */
export interface AssignmentListResponse {
  assignments: Assignment[]
  total: number
  page: number
  pageSize: number
}

/**
 * リスト項目（企業情報）
 */
export interface ListItem {
  id: number
  listId: number
  companyName: string
  companyUrl?: string
  contactEmail?: string
  contactName?: string
  notes?: string
  status: 'pending' | 'completed' | 'failed'
  createdAt: string
  updatedAt: string
}

/**
 * 割り当て詳細（企業情報とスクリプト付き）
 */
export interface AssignmentDetail extends Assignment {
  listItems: ListItem[]
  script?: {
    title: string
    content: string
  }
  projectDescription?: string
}
