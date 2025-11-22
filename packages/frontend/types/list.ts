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

/**
 * 検収ステータス
 */
export type InspectionStatus =
  | 'not_started' // 未検収
  | 'in_progress' // 検収中
  | 'completed' // 検収完了
  | 'rejected' // 却下

/**
 * 検収情報
 */
export interface Inspection {
  id: string
  listId: string
  status: InspectionStatus
  inspectedBy?: string // 検収者
  inspectedAt?: string // 検収日時
  comment?: string // コメント
  createdAt: string
  updatedAt: string
}
