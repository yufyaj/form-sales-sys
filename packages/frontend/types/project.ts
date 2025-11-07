/**
 * プロジェクト関連の型定義
 */

/**
 * プロジェクトステータス
 */
export type ProjectStatus = 'planning' | 'active' | 'paused' | 'completed' | 'archived'

/**
 * プロジェクト
 */
export interface Project {
  id: string
  name: string
  description?: string
  customerId: string
  customerName: string // 顧客名（結合済み）
  status: ProjectStatus
  progress: number // 0-100の進捗率
  totalLists: number // 総リスト数
  completedLists: number // 完了リスト数
  totalSubmissions: number // 総送信数
  createdAt: string
  updatedAt: string
}

/**
 * プロジェクト一覧のレスポンス
 */
export interface ProjectListResponse {
  projects: Project[]
  total: number
  page: number
  pageSize: number
}

/**
 * プロジェクト作成フォームデータ
 */
export interface CreateProjectFormData {
  name: string
  description?: string
  customerId: string
}

/**
 * プロジェクト更新フォームデータ
 */
export interface UpdateProjectFormData {
  name?: string
  description?: string
  status?: ProjectStatus
}
