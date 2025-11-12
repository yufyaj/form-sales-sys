/**
 * 顧客管理関連の型定義
 *
 * バックエンドの ClientOrganization と ClientContact エンティティに対応
 */

/**
 * 顧客組織
 *
 * Organizations テーブルと 1:1 の関係を持つ顧客企業の詳細情報
 */
export interface ClientOrganization {
  id: number
  organizationId: number // Organizations.id への外部キー
  organizationName: string // 組織名（Organizations.name から取得）
  industry: string | null // 業種
  employeeCount: number | null // 従業員数
  annualRevenue: number | null // 年商（円）
  establishedYear: number | null // 設立年
  website: string | null // Webサイト
  salesPerson: string | null // 担当営業
  notes: string | null // 備考
  createdAt: string
  updatedAt: string
  deletedAt: string | null
}

/**
 * 顧客担当者
 *
 * 顧客組織内の担当者情報（ClientOrganization との N:1 関係）
 */
export interface ClientContact {
  id: number
  clientOrganizationId: number // ClientOrganizations.id への外部キー
  fullName: string // 氏名（必須）
  department: string | null // 部署
  position: string | null // 役職
  email: string | null // メールアドレス
  phone: string | null // 電話番号
  mobile: string | null // 携帯電話番号
  isPrimary: boolean // 主担当フラグ
  notes: string | null // 備考
  createdAt: string
  updatedAt: string
  deletedAt: string | null
}

/**
 * 顧客組織の詳細（担当者リスト付き）
 *
 * 顧客詳細画面などで使用
 */
export interface ClientOrganizationDetail extends ClientOrganization {
  contacts: ClientContact[]
}

/**
 * 顧客組織作成リクエスト
 */
export interface CreateClientOrganizationRequest {
  organizationId: number
  industry?: string
  employeeCount?: number
  annualRevenue?: number
  establishedYear?: number
  website?: string
  salesPerson?: string
  notes?: string
}

/**
 * 顧客組織更新リクエスト
 */
export interface UpdateClientOrganizationRequest {
  industry?: string
  employeeCount?: number
  annualRevenue?: number
  establishedYear?: number
  website?: string
  salesPerson?: string
  notes?: string
}

/**
 * 顧客担当者作成リクエスト
 */
export interface CreateClientContactRequest {
  clientOrganizationId: number
  fullName: string
  department?: string
  position?: string
  email?: string
  phone?: string
  mobile?: string
  isPrimary?: boolean
  notes?: string
}

/**
 * 顧客担当者更新リクエスト
 */
export interface UpdateClientContactRequest {
  fullName?: string
  department?: string
  position?: string
  email?: string
  phone?: string
  mobile?: string
  isPrimary?: boolean
  notes?: string
}

/**
 * 顧客組織一覧のフィルタ条件
 */
export interface ClientOrganizationFilter {
  industry?: string
  salesPerson?: string
  minEmployeeCount?: number
  maxEmployeeCount?: number
  minAnnualRevenue?: number
  maxAnnualRevenue?: number
  searchTerm?: string // 組織名での検索
}

/**
 * 顧客組織のソート条件
 */
export type ClientOrganizationSortKey =
  | 'organizationName'
  | 'industry'
  | 'employeeCount'
  | 'annualRevenue'
  | 'establishedYear'
  | 'createdAt'
  | 'updatedAt'

export type SortDirection = 'asc' | 'desc'

export interface ClientOrganizationSort {
  key: ClientOrganizationSortKey
  direction: SortDirection
}

/**
 * ページネーション
 */
export interface Pagination {
  page: number
  limit: number
  total: number
}

/**
 * 顧客組織一覧レスポンス
 */
export interface ClientOrganizationListResponse {
  data: ClientOrganization[]
  pagination: Pagination
}

/**
 * フォームデータ型（バリデーションスキーマから推論）
 * 実際の型定義は lib/validations/customer.ts で行われる
 */
export type {
  CreateClientOrganizationFormData,
  UpdateClientOrganizationFormData,
  CreateClientContactFormData,
  UpdateClientContactFormData,
} from '@/lib/validations/customer'
