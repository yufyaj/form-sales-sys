/**
 * ワーカー質問管理関連の型定義
 *
 * バックエンドの WorkerQuestion エンティティに対応
 */

/**
 * 質問ステータス
 */
export type QuestionStatus = 'pending' | 'in_review' | 'answered' | 'closed'

/**
 * 質問優先度
 */
export type QuestionPriority = 'low' | 'medium' | 'high'

/**
 * ワーカー質問
 */
export interface WorkerQuestion {
  id: number
  workerId: number
  organizationId: number
  clientOrganizationId: number | null
  title: string
  content: string
  status: QuestionStatus
  priority: QuestionPriority
  answer: string | null
  answeredByUserId: number | null
  answeredAt: string | null
  tags: string | null
  internalNotes: string | null
  createdAt: string
  updatedAt: string
  deletedAt: string | null
}

/**
 * ワーカー質問作成リクエスト
 */
export interface CreateWorkerQuestionRequest {
  title: string
  content: string
  clientOrganizationId?: number | null
  priority?: QuestionPriority
  tags?: string | null
}

/**
 * ワーカー質問一覧レスポンス
 */
export interface WorkerQuestionListResponse {
  questions: WorkerQuestion[]
  total: number
  skip: number
  limit: number
}

/**
 * フォームデータ型（バリデーションスキーマから推論）
 */
export type {
  CreateWorkerQuestionFormData,
} from '@/lib/validations/question'
