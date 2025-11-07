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

/**
 * プロジェクト名をサニタイズする
 * 制御文字を削除し、最大長を100文字に制限
 */
export function sanitizeProjectName(name: string): string {
  if (!name) return ''
  // 最大長制限（100文字）
  const truncated = name.slice(0, 100)
  // 制御文字を削除
  const cleaned = truncated.replace(/[\x00-\x1F\x7F-\x9F]/g, '')
  return cleaned || ''
}

/**
 * プロジェクト説明をサニタイズする
 * 制御文字を削除し、最大長を500文字に制限
 */
export function sanitizeDescription(description: string | undefined): string | undefined {
  if (!description) return undefined
  // 最大長制限（500文字）
  const truncated = description.slice(0, 500)
  // 制御文字を削除
  const cleaned = truncated.replace(/[\x00-\x1F\x7F-\x9F]/g, '')
  return cleaned || undefined
}
