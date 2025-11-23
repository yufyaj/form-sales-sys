/**
 * ワーカー質問関連の型定義
 *
 * バックエンドのワーカー質問スキーマに対応するフロントエンドの型定義
 */

/**
 * 質問ステータス
 */
export enum QuestionStatus {
  PENDING = "pending",
  IN_REVIEW = "in_review",
  ANSWERED = "answered",
  CLOSED = "closed",
}

/**
 * 質問優先度
 */
export enum QuestionPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  URGENT = "urgent",
}

/**
 * ワーカー質問情報
 */
export interface WorkerQuestion {
  id: number;
  workerId: number;
  organizationId: number;
  clientOrganizationId: number | null;
  title: string;
  content: string;
  status: QuestionStatus;
  priority: QuestionPriority;
  answer: string | null;
  answeredByUserId: number | null;
  answeredAt: string | null;
  tags: string | null;
  internalNotes: string | null;
  createdAt: string;
  updatedAt: string;
  deletedAt: string | null;
}

/**
 * 質問作成リクエスト
 */
export interface WorkerQuestionCreateRequest {
  title: string;
  content: string;
  clientOrganizationId?: number | null;
  priority?: QuestionPriority;
  tags?: string | null;
}

/**
 * 質問更新リクエスト
 */
export interface WorkerQuestionUpdateRequest {
  title?: string | null;
  content?: string | null;
  status?: QuestionStatus | null;
  priority?: QuestionPriority | null;
  tags?: string | null;
  internalNotes?: string | null;
}

/**
 * 回答追加リクエスト
 */
export interface WorkerQuestionAnswerRequest {
  answer: string;
}

/**
 * 質問一覧レスポンス
 */
export interface WorkerQuestionListResponse {
  questions: WorkerQuestion[];
  total: number;
  skip: number;
  limit: number;
}

/**
 * 未読数レスポンス
 */
export interface UnreadCountResponse {
  unreadCount: number;
}

/**
 * 質問一覧取得パラメータ
 */
export interface WorkerQuestionListParams {
  skip?: number;
  limit?: number;
  status?: QuestionStatus;
  priority?: QuestionPriority;
  workerId?: number;
}

/**
 * 質問ステータスの日本語ラベル
 */
export const QuestionStatusLabel: Record<QuestionStatus, string> = {
  [QuestionStatus.PENDING]: "未対応",
  [QuestionStatus.IN_REVIEW]: "確認中",
  [QuestionStatus.ANSWERED]: "回答済み",
  [QuestionStatus.CLOSED]: "クローズ",
};

/**
 * 質問優先度の日本語ラベル
 */
export const QuestionPriorityLabel: Record<QuestionPriority, string> = {
  [QuestionPriority.LOW]: "低",
  [QuestionPriority.MEDIUM]: "中",
  [QuestionPriority.HIGH]: "高",
  [QuestionPriority.URGENT]: "緊急",
};

/**
 * 質問ステータスの色（Tailwind CSSクラス）
 */
export const QuestionStatusColor: Record<QuestionStatus, string> = {
  [QuestionStatus.PENDING]: "bg-yellow-100 text-yellow-800",
  [QuestionStatus.IN_REVIEW]: "bg-blue-100 text-blue-800",
  [QuestionStatus.ANSWERED]: "bg-green-100 text-green-800",
  [QuestionStatus.CLOSED]: "bg-gray-100 text-gray-800",
};

/**
 * 質問優先度の色（Tailwind CSSクラス）
 */
export const QuestionPriorityColor: Record<QuestionPriority, string> = {
  [QuestionPriority.LOW]: "bg-gray-100 text-gray-800",
  [QuestionPriority.MEDIUM]: "bg-blue-100 text-blue-800",
  [QuestionPriority.HIGH]: "bg-orange-100 text-orange-800",
  [QuestionPriority.URGENT]: "bg-red-100 text-red-800",
};
