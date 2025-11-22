/**
 * NGリストドメイン関連の型定義
 */

/**
 * NGリストドメイン
 */
export interface NgListDomain {
  id: number
  listId: number
  domain: string // 元のドメインパターン(ユーザー入力)
  domainPattern: string // 正規化されたドメインパターン(比較用)
  isWildcard: boolean // ワイルドカード使用フラグ
  memo?: string | null // メモ(任意)
  createdAt: string
  updatedAt: string
  deletedAt?: string | null
}

/**
 * NGリストドメイン一覧のレスポンス
 */
export interface NgListDomainListResponse {
  ngDomains: NgListDomain[]
  total: number
}

/**
 * NGリストドメイン作成リクエスト
 */
export interface NgListDomainCreateRequest {
  listId: number
  domain: string
  memo?: string | null
}

/**
 * NGリストドメインチェックリクエスト
 */
export interface NgListDomainCheckRequest {
  listId: number
  url: string
}

/**
 * NGリストドメインチェックレスポンス
 */
export interface NgListDomainCheckResponse {
  isNg: boolean
  matchedPattern?: string | null
  extractedDomain?: string | null
}

/**
 * NGリストドメイン作成フォームデータ
 */
export interface NgListDomainFormData {
  domains: Array<{
    domain: string
    memo?: string
  }>
}
