/**
 * リストスクリプト関連の型定義
 */

/**
 * リストスクリプト
 */
export interface ListScript {
  id: number
  listId: number
  title: string // スクリプトタイトル（件名）
  content: string // スクリプト本文
  createdAt: string
  updatedAt: string
  deletedAt?: string | null
}

/**
 * リストスクリプト一覧のレスポンス
 */
export interface ListScriptListResponse {
  scripts: ListScript[]
  total: number
}

/**
 * リストスクリプト作成リクエスト
 */
export interface ListScriptCreateRequest {
  listId: number
  title: string
  content: string
}

/**
 * リストスクリプト更新リクエスト
 */
export interface ListScriptUpdateRequest {
  title?: string
  content?: string
}

/**
 * リストスクリプト作成フォームデータ
 */
export interface ListScriptFormData {
  scripts: Array<{
    title: string
    content: string
  }>
}
