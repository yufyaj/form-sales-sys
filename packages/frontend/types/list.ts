/**
 * リスト関連の型定義
 */

/**
 * リストステータス
 */
export type ListStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

/**
 * リスト
 */
export interface List {
  id: string
  name: string
  description?: string
  projectId: string
  projectName: string // プロジェクト名（結合済み）
  status: ListStatus
  totalRecords: number // 総レコード数
  processedRecords: number // 処理済みレコード数
  successCount: number // 成功数
  failureCount: number // 失敗数
  createdAt: string
  updatedAt: string
}

/**
 * リスト一覧のレスポンス
 */
export interface ListResponse {
  lists: List[]
  total: number
  page: number
  pageSize: number
}

/**
 * リスト作成フォームデータ
 */
export interface CreateListFormData {
  name: string
  description?: string
  projectId: string
}
